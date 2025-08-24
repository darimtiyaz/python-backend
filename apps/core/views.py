from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .services import ProductService
from .serializers import (
    ProductSerializer, ProductCreateSerializer, 
    ProductUpdateSerializer, ProductListSerializer
)

from rest_framework.parsers import MultiPartParser, FormParser
from .services import MediaService
from .serializers import MediaFileSerializer, FileUploadSerializer


class ProductListView(APIView):
    def get(self, request):
        # Get query parameters
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('pageSize', 10))
        search = request.GET.get('search', '')
        sort_by = request.GET.get('sortBy', '-created_at')
        
        # Build filters from query parameters
        filters = {
            'type': request.GET.get('type'),
            'category': request.GET.get('category'),
        }
        
        product_service = ProductService()
        
        # Get filtered and sorted products
        products_queryset = product_service.get_all_products(filters, search, sort_by)
        
        # Get paginated results
        result = product_service.get_paginated_products(products_queryset, page, page_size)
        
        # Serialize the products
        serializer = ProductListSerializer(result['products'], many=True)
        
        return Response({
            'products': serializer.data,
            'pagination': result['pagination']
        }, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = ProductCreateSerializer(data=request.data)
        print("seriable dataaaaaaaaaaa ", serializer)
        if serializer.is_valid():
            product_service = ProductService()
            product = product_service.create_product(serializer.validated_data, request.auth_user)
            
            response_serializer = ProductSerializer(product)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ProductDetailView(APIView):
    def get(self, request, product_id):
        product_service = ProductService()
        product = product_service.get_product_by_id(product_id)
        
        if not product:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, product_id):
        product_service = ProductService()
        product = product_service.get_product_by_id(product_id)
        
        if not product:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user owns the product
        if product.created_by != request.auth_user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ProductUpdateSerializer(product, data=request.data)
        if serializer.is_valid():
            updated_product = product_service.update_product(product_id, serializer.validated_data)
            response_serializer = ProductSerializer(updated_product)
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, product_id):
        product_service = ProductService()
        product = product_service.get_product_by_id(product_id)
        
        if not product:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if user owns the product
        if product.created_by != request.auth_user:
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        product_service.delete_product(product_id)
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_200_OK)

class MediaUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        media_service = MediaService()
        uploaded_files = []
        
        # Handle single file upload
        if 'file' in request.FILES:
            uploaded_file = media_service.upload_file(request.FILES['file'], request.auth_user)
            uploaded_files.append(uploaded_file)
        
        # Handle multiple files upload
        if 'files' in request.FILES:
            multiple_files = media_service.upload_multiple_files(request.FILES.getlist('files'), request.auth_user)
            uploaded_files.extend(multiple_files)
        
        # Serialize the response
        response_serializer = MediaFileSerializer(uploaded_files, many=True)
        
        return Response({
            'message': 'Files uploaded successfully',
            'uploaded_files': response_serializer.data,
            'total_files': len(uploaded_files)
        }, status=status.HTTP_201_CREATED)