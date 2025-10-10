from django.db import models

# Create your models here.

class ActiveCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Category(models.Model):
    name=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True,null=True)
    image=models.ImageField(upload_to="categories/",blank=True,null=True)
    is_deleted=models.BooleanField(default=False)
    objects=ActiveCategoryManager()
    all_category=models.Manager()


    def __str__(self):
        return self.name


class ActiveProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Products(models.Model):
    STATUS=[
        ("Published","published"),
        ("Out of stock","outofstock"),
        ("Low stock","lowstock")
    ]
    category=models.ForeignKey(Category,related_name="products",on_delete=models.CASCADE)
    is_deleted=models.BooleanField(default=False)
    name=models.CharField(max_length=100)
    description=models.TextField(blank=True,null=True) 
    status=models.CharField(choices=STATUS)
    objects=ActiveProductManager()
    all_products=models.Manager()

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    UNIT=[
        ("g","gram"),
        ("kg","kilogram")
    ]
    product=models.ForeignKey(Products,related_name="variants",on_delete=models.CASCADE)
    weight=models.IntegerField()
    unit=models.CharField(choices=UNIT)
    quantity_stock=models.IntegerField(default=0)
    price=models.DecimalField(max_digits=10,decimal_places=2) 
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.product.name} is {self.weight}{self.unit}"
    
class ProductImage(models.Model):
    product=models.ForeignKey(Products,related_name="images",on_delete=models.CASCADE)
    image=models.ImageField(upload_to="products/")

    def __str__(self):
        return f"{self.product.name} image"