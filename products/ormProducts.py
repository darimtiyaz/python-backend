from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.productModel import Product
import mongoengine as me

ormProducts_bp = Blueprint('ormProducts', __name__)

@ormProducts_bp.route('/create', methods=['POST'])
@jwt_required()
def create_product():
    try:
        user_id = get_jwt_identity()
        data = request.json
        name = data.get('name')
        description = data.get('description')
        qty = data.get('qty')

        if not name or not description or not qty:
            return jsonify({"message": "Please fill all required fields"}), 400

        product = Product(
            user_id=user_id,
            name=name,
            description=description,
            qty=qty
        )
        product.save()

        return jsonify({"message": "Product created successfully"}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@ormProducts_bp.route('/', methods=['GET'])
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

        query = Product.objects(user_id=user_id)
        if search_query:
            query = query.filter(
                me.Q(name__icontains=search_query) |
                me.Q(description__icontains=search_query)
            )

        # Selecting specific fields
        if fields:
            fields = fields.split(',')
            query = query.only(*fields)

        # Sorting and Pagination
        query = query.order_by(sort_by if sort_order == 1 else f'-{sort_by}')
        skip = (page - 1) * limit
        products = query.skip(skip).limit(limit)

        total_count = Product.objects(user_id=user_id).count()
        total_pages = (total_count + limit - 1) // limit

        products_list = [
            {
                **product.to_mongo().to_dict(),
                '_id': str(product.id)
            }
            for product in products
        ]
        return jsonify({
            "message": "Products fetched successfully",
            "data": products_list,
            "totalPages": total_pages,
            "currentPage": page,
            "totalCount": total_count
        }), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@ormProducts_bp.route('/get/<id>', methods=['GET'])
@jwt_required()
def getSingle_product(id):
    try:
        user_id = get_jwt_identity()

        product = Product.objects(id=id, user_id=user_id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404
        item = product.to_mongo().to_dict()
        item["_id"] = str(item["_id"])
        return jsonify({"message": "Product updated successfully", "data": item}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@ormProducts_bp.route('/update/<id>', methods=['PATCH'])
@jwt_required()
def update_product(id):
    try:
        user_id = get_jwt_identity()
        data = request.json
        name = data.get('name')
        description = data.get('description')
        qty = data.get('qty')

        if not name or not description or not qty:
            return jsonify({"message": "Please fill all required fields"}), 400

        product = Product.objects(id=id, user_id=user_id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404

        product.update(
            set__name=name,
            set__description=description,
            set__qty=qty
        )
        updated_product = Product.objects(id=id, user_id=user_id).first()
        item = updated_product.to_mongo().to_dict()
        item["_id"] = str(item["_id"])
        return jsonify({"message": "Product updated successfully", "product": item}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@ormProducts_bp.route('/delete/<id>', methods=['DELETE'])
@jwt_required()
def delete_product(id):
    try:
        user_id = get_jwt_identity()
        product = Product.objects(id=id, user_id=user_id).first()
        if not product:
            return jsonify({"message": "Product not found"}), 404

        product.delete()

        return jsonify({"message": "Product deleted successfully"}), 200
    except Exception as e:
        return jsonify({"message": str(e)}), 500

