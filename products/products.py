from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query, Request
from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from config import db
from utils.utils import get_current_user2

from fastapi.responses import JSONResponse
from uuid import uuid4
import os
from fastapi.security import OAuth2PasswordBearer
from pymongo.errors import PyMongoError
from typing import Optional, List

router = APIRouter()

class Product(BaseModel):
    title: str = Field(...)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    user_id: Optional[str] = None

class ProductUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    price: Optional[float]    

@router.post("/create", response_model=Product)
async def create_product(product: Product, current_user: dict = Depends(get_current_user2)):
    try:
        product.user_id = current_user["_id"]
        product_dict = product.dict()
        result = await db.products.insert_one(product_dict)
        product_dict["_id"] = str(result.inserted_id)
        return product_dict
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating product") from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred") from e


@router.get("/get/{product_id}", response_model=Product)
async def get_product(product_id: str, current_user: dict = Depends(get_current_user2)):
    try:
        product = await db.products.find_one({"_id": ObjectId(product_id), "user_id": current_user["_id"]})
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found")
        product["_id"] = str(product["_id"])
        return product
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching product") from e
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred") from e


@router.patch("/update/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate, current_user: dict = Depends(get_current_user2)):
    try:
        product = await db.products.find_one({"_id": ObjectId(product_id), "user_id": current_user["_id"]})
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
        updated_product = {k: v for k, v in product_update.dict().items() if v is not None}
        if updated_product:
            result = await db.products.find_one_and_update(
                {"_id": ObjectId(product_id), "user_id": current_user["_id"]},
                {"$set": updated_product},
                return_document=True
            )
            result["_id"] = str(result["_id"])
            return result
        return product
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating product") from e
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred") from e

@router.delete("/delete/{product_id}")
async def delete_product(product_id: str, current_user: dict = Depends(get_current_user2)):
    try:
        product = await db.products.find_one({"_id": ObjectId(product_id), "user_id": current_user["_id"]})
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
        await db.products.delete_one({"_id": ObjectId(product_id), "user_id": current_user["_id"]})
        return {"detail": "Product deleted"}
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting product") from e
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred") from e

@router.get("/get-all", response_model=Dict[str, Any])
async def get_all_products(
    search: Optional[str] = None,
    sort_by: Optional[str] = "title",
    order: Optional[int] = 1,  # 1 for ascending, -1 for descending
    limit: Optional[int] = 10,  # Number of products per page
    page: Optional[int] = 1,  # Current page number
    fields: Optional[str] = None,
    current_user: dict = Depends(get_current_user2)
):
    try:
        query = {"user_id": current_user["_id"]}

        # Handle searching by title or description
        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]

        # Handle projection fields
        projection = None
        if fields:
            projection = {field: 1 for field in fields.split(",")}
            projection["_id"] = 1  # Always include the _id field

        # Get total count of products that match the query
        total_count = await db.products.count_documents(query)

        # Handle pagination
        skip = (page - 1) * limit  # Calculate the number of documents to skip based on page number

        cursor = db.products.find(query, projection=projection).sort(sort_by, order).skip(skip).limit(limit)
        products = await cursor.to_list(length=limit)

        for product in products:
            product["_id"] = str(product["_id"])

        # Calculate total number of pages
        total_pages = (total_count + limit - 1) // limit  # Use ceiling division

        return {
            "products": products,
            "total_count": total_count,
            "total_pages": total_pages,
            "current_page": page
        }

    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error fetching products") from e
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred") from e

UPLOAD_DIRECTORY = "uploads/"
@router.post("/upload-photo")
async def upload_photo(file: UploadFile = File(...), current_user: dict = Depends(get_current_user2)):
    try:
        # Validate file type
        if not os.path.exists(UPLOAD_DIRECTORY):
            os.makedirs(UPLOAD_DIRECTORY)

        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Only image files are allowed.")

        # Generate unique file name
        file_extension = file.filename.split(".")[-1]
        unique_filename = f"{uuid4()}.{file_extension}"
        file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

        # Save the file
        try:
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
        except Exception as e:
            raise HTTPException(status_code=500, detail="Error saving file") from e

        file_url = f"/{UPLOAD_DIRECTORY}{unique_filename}"

        # Save the file URL to the database
        try:
            result = await db.users.update_one(
                {"_id": ObjectId(current_user["_id"])},
                {"$set": {"photo_url": file_url}}
            )
            if result.modified_count == 0:
                raise HTTPException(status_code=500, detail="Failed to update user record with photo URL")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database update error") from e

        return JSONResponse(content={"url": file_url})

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

