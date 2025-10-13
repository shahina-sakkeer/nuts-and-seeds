from django.contrib import admin
from .models import Category,Products,ProductVariant,ProductImage
# Register your models here.

admin.site.register(Category)
admin.site.register(Products)
admin.site.register(ProductVariant)
admin.site.register(ProductImage)