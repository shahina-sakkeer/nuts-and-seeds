from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
import re
from django.core.exceptions import ValidationError


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
