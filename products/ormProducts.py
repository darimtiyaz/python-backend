from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status, Query, Request
from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
from config import db
from utils.utils import get_current_user2
from models.productModel import Products
from models.authModel import Auth
from fastapi.responses import JSONResponse
from uuid import uuid4
import os
from fastapi.security import OAuth2PasswordBearer
from pymongo.errors import PyMongoError
from typing import Optional, List
import json
from mongoengine import DoesNotExist, Q
from datetime import datetime

router = APIRouter()

class Product(BaseModel):
    id: Optional[str] = None
    title: str = Field(...)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    user_id: Optional[str] = None
    created_at: Optional[datetime] = None  # Add created_at field
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ProductUpdate(BaseModel):
    title: Optional[str]
    description: Optional[str]
    price: Optional[float]    

@router.post("/create", response_model=Product)
async def create_product(product: Product, current_user: dict = Depends(get_current_user2)):
    try:
        product.user_id = current_user["id"]
        result = Products(title=product.title, description=product.description, price=product.price, user_id=product.user_id)
        new_product = result.save()
        new_product['id'] = str(new_product['id'])
        return new_product
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating product") from e
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred") from e


@router.get("/get/{product_id}", response_model=Product)
async def get_product(product_id: str, current_user: dict = Depends(get_current_user2)):
    try:
        product = Products.objects.filter(id=product_id, user_id=current_user["id"]).first()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        product['id'] = str(product.id)
        return product
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred") from e


@router.patch("/update/{product_id}", response_model=Product)
async def update_product(product_id: str, product_update: ProductUpdate, current_user: dict = Depends(get_current_user2)):
    try:
        product = Products.objects.filter(id=product_id, user_id=current_user["id"]).first()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        product.update(
            set__title=product_update.title,
            set__description=product_update.description,
            set__price=product_update.price,
        )
        updated_product = Products.objects.filter(id=product_id, user_id=current_user["id"]).first()
        updated_product['id'] = str(updated_product.id) 
        return updated_product
              
    except PyMongoError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating product") from e
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred") from e

@router.delete("/delete/{product_id}")
async def delete_product(product_id: str, current_user: dict = Depends(get_current_user2)):
    try:
        product = Products.objects.filter(id=product_id, user_id=current_user["id"]).first()
        if product is None:
            raise HTTPException(status_code=404, detail="Product not found or unauthorized")
        
        product.delete()
        return {"detail": "Product deleted"}
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected errorffffffffffffffffff occurred") from e

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
        query = Q(user_id=current_user["id"])

        if search:
            query &= Q(title__icontains=search) | Q(description__icontains=search)

        skip = (page - 1) * limit  # Calculate the number of documents to skip based on page number
        products_query = (
            Products.objects(query)
            .order_by(f"{'-' if order == -1 else ''}{sort_by}")
            .skip(skip)
            .limit(limit)
        )

        # Select specific fields if projection is provided
        if fields:
            products_query = products_query.only(*fields.split(","))

        # Get total count of products that match the query
        total_count = Products.objects(query).count()

        products = products_query  # Execute the query
        products_dict = []
        # Calculate total number of pages
        total_pages = (total_count + limit - 1) // limit 
        return {
            "products": json.loads(products.to_json()),
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
            result = Auth.objects.filter(id=current_user["id"]).update_one(set__photo_url=file_url, set__updated_at=datetime.utcnow())
            if result == 0:
                raise HTTPException(status_code=500, detail="Failed to update user record with photo URL")
        except Exception as e:
            raise HTTPException(status_code=500, detail="Database update error") from e

        return JSONResponse(content={"url": file_url})

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred") from e

