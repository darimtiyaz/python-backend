from django.db import models
from django.conf import settings
import os
import uuid

class Product(models.Model):
    PRODUCT_TYPES = [
        ('physical', 'Physical'),
        ('digital', 'Digital'),
        ('service', 'Service'),
    ]
    
    CATEGORIES = [
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing'),
        ('books', 'Books'),
        ('food', 'Food & Beverages'),
        ('furniture', 'Furniture'),
        ('sports', 'Sports'),
        ('beauty', 'Beauty & Health'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=PRODUCT_TYPES)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name

def upload_to(instance, filename):
    # Generate unique filename
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4().hex}.{ext}"
    return os.path.join('uploads', filename)

class MediaFile(models.Model):
    file = models.FileField(upload_to=upload_to)
    original_name = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField()
    mime_type = models.CharField(max_length=100)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return self.original_name
    
    def get_file_url(self):
        return self.file.url
