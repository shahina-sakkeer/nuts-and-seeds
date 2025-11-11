from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
import re
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryField
from admin_app.models import ProductVariant,Products
import uuid


# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("Email is required")
        email=self.normalize_email(email)
        user=self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser,PermissionsMixin):
    email=models.EmailField(unique=True)
    firstname=models.CharField(max_length=100)
    lastname=models.CharField(max_length=100,blank=True)
    phone_number=models.CharField(max_length=15,unique=True)
    is_active=models.BooleanField(default=True)
    is_admin=models.BooleanField(default="False")
    is_blocked=models.BooleanField(default="False")
    is_staff=models.BooleanField(default="False")
    is_superuser=models.BooleanField(default="False")
    date_joined=models.DateTimeField(auto_now_add=True)

    objects=CustomUserManager()

    USERNAME_FIELD="email"
    REQUIRED_FIELDS=["firstname","phone_number"]

    def __str__(self):
        return self.email
    
    def clean(self):
        super().clean()
        phone_pattern=re.compile(r'^\+?1?\d{9,15}$|^(\d{3}[-.\s]?)?\d{3}[-.\s]?\d{4}$')
        if self.phone_number and not phone_pattern.match(self.phone_number):
            raise ValidationError({"phone_number": "Invalid phone number format."})
        
        

class UserAddress(models.Model):
    user=models.ForeignKey(CustomUser,related_name="useraddress",on_delete=models.CASCADE)
    house_name=models.CharField(max_length=200)
    street=models.CharField(max_length=50)
    landmark=models.CharField(max_length=100)
    city=models.CharField(max_length=50)
    pincode=models.IntegerField()
    state=models.CharField(max_length=50)
    image=CloudinaryField('image', blank=True,null=True)
    created_at=models.DateField(auto_now_add=True)
    updated_at=models.DateField(auto_now=True)
    is_deleted=models.BooleanField(default=False)
    is_primary=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.firstname} is {self.house_name}"
    

class Cart(models.Model):
    user=models.ForeignKey(CustomUser,related_name="cart",on_delete=models.CASCADE)
    created_at=models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.firstname}"
    

class CartItem(models.Model):
    cart=models.ForeignKey(Cart,related_name="cart_item",on_delete=models.CASCADE)
    product=models.ForeignKey(ProductVariant,related_name="cart_product",on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.cart.user.firstname}"


def generate_orderID():
    return str(uuid.uuid4()).split('-')[0].upper()

class Orders(models.Model):
    PAYMENT_METHOD_CHOICES=[
        ('cash_on_delivery','Cash on delivery'),
        ('razorpay','Razor pay'),
        ('wallet','Wallet')
    ]
    orderID=models.CharField(max_length=20,unique=True, default=generate_orderID)
    user=models.ForeignKey(CustomUser,related_name="orderuser",on_delete=models.CASCADE)
    address=models.ForeignKey(UserAddress,related_name="orderaddress",on_delete=models.CASCADE)
    item_count=models.PositiveIntegerField()
    total_price=models.DecimalField(max_digits=10,decimal_places=2)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    is_deleted=models.BooleanField(default=0)
    payment_method=models.CharField(choices=PAYMENT_METHOD_CHOICES,default="cash_on_delivery")
    delivery_charge=models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    discount=models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    razorpay_order_id=models.CharField(max_length=255,blank=True,null=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"order {self.orderID} by {self.user.firstname}"


class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('order_recieved','Order Recieved'),
        ('packed','Packed'),
        ('shipped','Shipped'),
        ('in Transit','In transit'),
        ('delivered','Delivered'),
        ('cancelled','Cancelled'),
        ('returned','Returned'),
        ('rejected','Rejected'),
        ('payment_pending','Payment Pending')
    ]
    APPROVAL_STATUS_CHOICES = [
        ('pending','Pending'),
        ('refunded','Refunded'),
        ('rejected','Rejected'),
    ]
    order=models.ForeignKey(Orders,related_name="orderitem",on_delete=models.CASCADE)
    product=models.ForeignKey(ProductVariant,related_name="item",on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField()
    unit_price=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    cancellation_reason=models.TextField(blank=True,null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20,
    choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],
    default='pending')
    approval_status = models.CharField(max_length=20, choices=APPROVAL_STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.product}"
    

class OrderReturn(models.Model):
    RETURN_CHOICES=[
        ('defective_product','Defective Product'),
        ('wrong_item','Wrong Item'),
        ('other','other')
    ]
    APPROVAL_CHOICES = [
        ('pending','Pending'),
        ('refunded','Refunded'),
        ('rejected','Rejected'),
    ]
    user=models.ForeignKey(CustomUser,related_name="user_return",on_delete=models.CASCADE)
    item=models.OneToOneField(OrderItem,related_name='returnitem',on_delete=models.CASCADE)
    return_choice=models.CharField(max_length=100,choices=RETURN_CHOICES,blank=True,null=True)
    approval_status=models.CharField(max_length=200,choices=APPROVAL_CHOICES,default="pending",blank=True,null=True)
    return_reason=models.TextField()
    image=CloudinaryField('return_image',blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ReturnRequest for {self.item.product.product.name} - {self.approval_status}"


class Wallet(models.Model):
    user=models.ForeignKey(CustomUser,related_name="walletuser",on_delete=models.CASCADE)
    balance=models.DecimalField(max_digits=10,decimal_places=2,default=0.00)

    def __str__(self):
        return f"{self.user.firstname}'s wallet has Rs.{self.balance} as balance"
    

class WalletTransaction(models.Model):
    wallet=models.ForeignKey(Wallet,related_name="transaction",on_delete=models.CASCADE)
    amount=models.DecimalField(max_digits=10,decimal_places=2,default=0)
    transaction_type=models.CharField(max_length=200, choices=[
        ('credit','credit'),('debit','debit')
    ])
    is_paid=models.BooleanField(default=False)
    razorpay_order_id=models.CharField(max_length=255,blank=True,null=True)
    created_at=models.DateTimeField(auto_now=True)


class Wishlist(models.Model):
    user=models.ForeignKey(CustomUser,related_name="userwishlist",on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)



class WishlistItem(models.Model):
    wishlist=models.ForeignKey(Wishlist,related_name="wishlistitem",on_delete=models.CASCADE)
    product=models.ForeignKey(ProductVariant,related_name="wishlist_product",on_delete=models.CASCADE)

    class Meta:
        unique_together=('wishlist','product')

    def __str__(self):
        return f"{self.product.name} in wishlist"
    












