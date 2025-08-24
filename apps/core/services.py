from .repositories.product_repository import ProductRepository

class ProductService:
    def __init__(self):
        self.product_repository = ProductRepository()
    
    def get_all_products(self, filters=None, search=None, sort_by='-created_at'):
        return self.product_repository.get_all_products(filters, search, sort_by)
    
    def get_product_by_id(self, product_id):
        return self.product_repository.get_product_by_id(product_id)
    
    def create_product(self, product_data, user):
        return self.product_repository.create_product(product_data, user)
    
    def update_product(self, product_id, product_data):
        return self.product_repository.update_product(product_id, product_data)
    
    def delete_product(self, product_id):
        return self.product_repository.delete_product(product_id)
    
    def get_paginated_products(self, queryset, page, page_size):
        return self.product_repository.get_products_paginated(queryset, page, page_size)