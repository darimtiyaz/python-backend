from django.urls import path
from .views import ProductListView, ProductDetailView, MediaUploadView

urlpatterns = [
    path('products/', ProductListView.as_view(), name='product_list'),
    path('products/<int:product_id>/', ProductDetailView.as_view(), name='product_detail'),
    path('products/upload/', MediaUploadView.as_view(), name='media_upload')
]