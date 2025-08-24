from .repositories.product_repository import ProductRepository
from .repositories.media_repository import MediaRepository

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

class MediaService:
    def __init__(self):
        self.media_repository = MediaRepository()
    
    def upload_file(self, uploaded_file, user):
        return self.media_repository.create_media_file(uploaded_file, user)
    
    def upload_multiple_files(self, uploaded_files, user):
        results = []
        for uploaded_file in uploaded_files:
            media_file = self.upload_file(uploaded_file, user)
            results.append(media_file)
        return results
    
    def get_file_url(self, file_id):
        media_file = self.media_repository.get_media_file_by_id(file_id)
        if media_file:
            return media_file.get_file_url()
        return None
    
    def delete_file(self, file_id):
        return self.media_repository.delete_media_file(file_id)