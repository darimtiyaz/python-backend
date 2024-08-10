# products.py
from flask import Blueprint, request, jsonify, current_app, make_response, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, unset_jwt_cookies, set_access_cookies
from datetime import timedelta
from bson import ObjectId
from flask_mail import Message
from werkzeug.utils import secure_filename
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
import io

products_bp = Blueprint('products', __name__)
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../uploads'))

@products_bp.route('/create', methods=['POST'])
@jwt_required()
def createProduct():
    try:
        user_id = get_jwt_identity()
        data = request.json
        name = data.get('name')
        description = data.get('description')
        qty = data.get('qty')

        if not name or not description or not qty:
            return jsonify({"message": "Please fill all required fields"}), 400

        current_app.mongo.db.products.insert_one({'user_id': user_id, 'name': name, 'description':description, 'qty': qty})

        return jsonify({"message": "Product created successfully"}), 201
    except Exception as e:
          return jsonify({"message": str(e)}), 500

@products_bp.route('/', methods=['GET'])
@jwt_required()
def get_products():
    try:
        user_id = get_jwt_identity()
        
        search_query = request.args.get('search', '')
        fields = request.args.get('select', '')
        sort_by = request.args.get('sortBy', 'name')
        sort_order = int(request.args.get('sortOrder', '1'))  # 1 for ASC, -1 for DESC
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))

        # Build the search filter
        search_filter = {'user_id': user_id}
        if search_query:
            search_filter['$or'] = [
                {'name': {'$regex': search_query, '$options': 'i'}},
                {'description': {'$regex': search_query, '$options': 'i'}}
            ]
        
        # Selecting specific fields
        projection = {field: 1 for field in fields.split(',')} if fields else None

        # Pagination calculations
        skip = (page - 1) * limit
        
        # Fetch the products with filtering, selecting, sorting, and pagination
        products_cursor = current_app.mongo.db.products.find(
            search_filter, projection
        ).sort(sort_by, sort_order).skip(skip).limit(limit)

        # Convert cursor to list
        products = []
        for product in products_cursor:
            product['_id'] = str(product['_id'])
            products.append(product)
        
        # Count total products for pagination
        total_count = current_app.mongo.db.products.count_documents(search_filter)
        total_pages = (total_count + limit - 1) // limit 

        return jsonify({
            "message": "Products fetched successfully",
            "data": products,
            "totalPages": total_pages,
            "currentPage": page,
            "totalCount": total_count
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@products_bp.route('/get/<id>', methods=['GET'])
@jwt_required()
def getSingleProduct(id):
    try:
        user_id = get_jwt_identity()
        singleProduct = current_app.mongo.db.products.find_one({'_id': ObjectId(id), 'user_id': user_id})
        if not singleProduct:
            return jsonify({"message": "Product not found"}), 400
        singleProduct["_id"] = str(singleProduct["_id"])
        return jsonify({"message": "Product fetched successfully", "data":singleProduct}), 201
    except Exception as e:
          return jsonify({"message": str(e)}), 500

@products_bp.route('/update/<id>', methods=['PATCH'])
@jwt_required()
def updateProduct(id):
    try:
        user_id = get_jwt_identity()
        data = request.json
        name = data.get('name')
        description = data.get('description')
        qty = data.get('qty')

        if not name or not description or not qty:
            return jsonify({"message": "Please fill all required fields"}), 400

        result = current_app.mongo.db.products.update_one({'_id': ObjectId(id), 'user_id': user_id}, {'$set':{'name': name, 'description':description, 'qty': qty}})

        if result.matched_count == 0:
            return jsonify({"message": "Product not found or not authorized to update"}), 404

        return jsonify({"message": "Product updated successfully"}), 201
    except Exception as e:
          return jsonify({"message": str(e)}), 500

@products_bp.route('/delete/<id>', methods=['DELETE'])
@jwt_required()
def deleteProduct(id):
    try:
        user_id = get_jwt_identity()
        result = current_app.mongo.db.products.delete_one({'_id': ObjectId(id), 'user_id': user_id})

        if result.deleted_count == 0:
            return jsonify({"message": "Product not found or not authorized to delete"}), 404

        return jsonify({"message": "Product deleted successfully"}), 201
    except Exception as e:
          return jsonify({"message": str(e)}), 500

@products_bp.route('/file/upload', methods=['POST'])
@jwt_required()
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400

        if file:
            # Ensure the upload directory exists
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
                
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            return jsonify({"message": "File uploaded successfully", "filename": filename}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500


@products_bp.route('/cloudinary/upload', methods=['POST'])
@jwt_required()
def upload_cloudinary_file():
    try:
        if 'file' not in request.files:
            return jsonify({"message": "No file part"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400

        # Upload to Cloudinary
        user_id = get_jwt_identity()
        file_stream = io.BytesIO(file.read())
        upload_result = cloudinary.uploader.upload(file_stream, folder='uploads')

        file_url = upload_result.get('url')

        # Save file URL and user_id to the database
        current_app.mongo.db.files.insert_one({
            'user_id': user_id,
            'file_url': file_url,
            'filename': secure_filename(file.filename)
        })

        return jsonify({"message": "File uploaded successfully", "file_url": file_url}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

