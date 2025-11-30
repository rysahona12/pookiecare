from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.validators import RegexValidator
import uuid


class CustomUserManager(BaseUserManager):
    """Custom user manager for User model."""
    
    def create_user(self, email, phone_number, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('The Email field must be set')
        if not phone_number:
            raise ValueError('The Phone Number field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, phone_number, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model for PookieCare application."""
    
    # Validator for Bangladeshi phone numbers (11 digits starting with 01)
    phone_regex = RegexValidator(
        regex=r'^01[0-9]{9}$',
        message="Phone number must be in the format: '01XXXXXXXXX'. 11 digits starting with 01."
    )
    
    # User ID (automatically generated UUID)
    user_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        unique=True
    )
    
    # Personal Information
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100)
    
    # Contact Information
    email = models.EmailField(unique=True, max_length=255)
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=11,
        unique=True,
        help_text="Enter 11-digit Bangladeshi phone number (e.g., 01999999999)"
    )
    
    # Address Information
    house_number = models.CharField(max_length=50)
    road_number = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=10)
    district = models.CharField(max_length=100)
    country = models.CharField(max_length=50, default='Bangladesh', editable=False)
    
    # Django required fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    
    # Set the custom manager
    objects = CustomUserManager()
    
    # Define the field to use for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'first_name', 'last_name', 'house_number', 
                       'road_number', 'postal_code', 'district']
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        """Return the full name of the user."""
        if self.middle_name:
            return f"{self.first_name} {self.middle_name} {self.last_name}"
        return f"{self.first_name} {self.last_name}"
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    def get_full_address(self):
        """Return the complete address."""
        return (f"House: {self.house_number}, Road: {self.road_number}, "
                f"Postal Code: {self.postal_code}, {self.district}, {self.country}")
