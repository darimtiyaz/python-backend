from django.db.models import Q
from ..models import Product

class ProductRepository:
    def get_all_products(self, filters=None, search=None, sort_by='-created_at'):
        queryset = Product.objects.all()
        
        # Apply filters
        if filters:
            for field, value in filters.items():
                if value:
                    queryset = queryset.filter(**{field: value})
        
        # Apply search
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__icontains=search)
            )
        
        # Apply sorting
        if sort_by:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_product_by_id(self, product_id):
        try:
            return Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return None
    
    def create_product(self, product_data, user):
        product_data['created_by'] = user
        return Product.objects.create(**product_data)
    
    def update_product(self, product_id, product_data):
        product = self.get_product_by_id(product_id)
        if product:
            for key, value in product_data.items():
                setattr(product, key, value)
            product.save()
            return product
        return None
    
    def delete_product(self, product_id):
        product = self.get_product_by_id(product_id)
        if product:
            product.delete()
            return True
        return False
    
    def get_products_paginated(self, queryset, page, page_size):
        total_records = queryset.count()
        total_pages = (total_records + page_size - 1) // page_size
        
        start = (page - 1) * page_size
        end = start + page_size
        
        products = queryset[start:end]
        
        return {
            'products': products,
            'pagination': {
                'currentPage': page,
                'pageSize': page_size,
                'totalPages': total_pages,
                'totalRecords': total_records,
                'hasNext': page < total_pages,
                'hasPrev': page > 1
            }
        }