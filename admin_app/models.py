from django.db import models
from cloudinary.models import CloudinaryField


# Create your models here.

class ActiveCategoryManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Category(models.Model):
    name=models.CharField(max_length=100,unique=True)
    description=models.TextField(blank=True,null=True)
    image=CloudinaryField('image', blank=True, null=True)
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
    status=models.CharField(max_length=20,choices=STATUS)
    objects=ActiveProductManager()
    all_products=models.Manager()

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    UNIT=[
        ("g","gram"),
        ("kg","kilogram")
    ]
    STATUS=[
        ("Published","published"),
        ("Out of stock","outofstock"),
        ("Low stock","lowstock")
    ]
    product=models.ForeignKey(Products,related_name="variants",on_delete=models.CASCADE)
    weight=models.IntegerField()
    unit=models.CharField(choices=UNIT)
    quantity_stock=models.IntegerField(default=0)
    price=models.DecimalField(max_digits=10,decimal_places=2) 
    status=models.CharField(max_length=20, choices=STATUS,default="Published")
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    is_deleted=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.product.name} is {self.weight}{self.unit}"
    
class ProductImage(models.Model):
    product=models.ForeignKey(Products,related_name="images",on_delete=models.CASCADE)
    image=CloudinaryField('image')

    def __str__(self):
        return f"{self.product.name} image"


class Coupon(models.Model):
    DISCOUNT_CHOICES=[
        ('percentage','Percentage'),
        ('flat','flat')
    ]
    code=models.CharField(max_length=10,unique=True)
    discount_value=models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    minimum_purchase_amount=models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    maximum_discount_limit=models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    usage_limit=models.IntegerField(blank=True,null=True)
    start_date=models.DateTimeField()
    end_date=models.DateTimeField()
    is_active=models.BooleanField(default=False)
    discount_type=models.CharField(max_length=20,choices=DISCOUNT_CHOICES)
    description=models.TextField(blank=True,null=True)

    def __str__(self):
        return self.code


class CouponUsage(models.Model):
    coupon=models.ForeignKey(Coupon,related_name="coupons",on_delete=models.CASCADE)
    user=models.ForeignKey('user_app.CustomUser',related_name="user",on_delete=models.CASCADE)
    used_count=models.IntegerField(default=0)


class CategoryOffer(models.Model):
    name=models.CharField(max_length=200,default="null")
    category=models.ForeignKey(Category,related_name="categoryoffer",on_delete=models.CASCADE)
    offer_percentage=models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    start_date=models.DateTimeField()
    end_date=models.DateTimeField()
    is_active=models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'end_date'])
        ]

    def __str__(self):
        return f"{self.category.name} has {self.offer_percentage} %"


class ProductOffer(models.Model):
    name=models.CharField(max_length=200,default="null")
    product=models.ForeignKey(Products,related_name="productoffer",on_delete=models.CASCADE)
    offer_percentage=models.DecimalField(max_digits=10,decimal_places=2,default=0.0)
    start_date=models.DateTimeField()
    end_date=models.DateTimeField()
    is_active=models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['is_active', 'end_date'])
        ]

    def __str__(self):
        return f"{self.product.name} has {self.offer_percentage} %"
    

class Banner(models.Model):
    name=models.CharField(max_length=200,null=True,blank=True)
    image=CloudinaryField('image')
    created_at=models.DateField(auto_now_add=True)







