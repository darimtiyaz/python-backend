from django.db import models
from django.conf import settings

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