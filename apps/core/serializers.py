from rest_framework import serializers
from .models import Product
from rest_framework import serializers
from .models import MediaFile

class ProductSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'type', 'category', 'cost', 'description',
            'created_by', 'created_by_email', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'type', 'category', 'cost', 'description']

class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['name', 'type', 'category', 'cost', 'description']

class ProductListSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'type', 'category', 'cost', 
            'created_by_email', 'created_at'
        ]


class MediaFileSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = MediaFile
        fields = ['id', 'original_name', 'url', 'file_size', 'mime_type', 'uploaded_at']
        read_only_fields = ['id', 'url', 'file_size', 'mime_type', 'uploaded_at']
    
    def get_url(self, obj):
        return obj.get_file_url()

class FileUploadSerializer(serializers.Serializer):
    files = serializers.ListField(
        child=serializers.FileField(max_length=100000, allow_empty_file=False),
        required=False
    )
    file = serializers.FileField(required=False, allow_empty_file=False)
    
    def validate(self, data):
        if 'files' not in data and 'file' not in data:
            raise serializers.ValidationError("Either 'file' or 'files' must be provided.")
        return data