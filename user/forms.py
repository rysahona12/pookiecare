from django import forms
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from .models import User


class UserProfileEditForm(forms.ModelForm):
    """Form for editing user profile information."""
    
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    middle_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Middle Name (Optional)'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    phone_number = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '01XXXXXXXXX'}),
        help_text='Enter 11-digit Bangladeshi phone number (e.g., 01999999999)'
    )
    house_number = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'House Number'})
    )
    road_number = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Road Number'})
    )
    postal_code = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Postal Code'})
    )
    district = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'District'})
    )
    
    class Meta:
        model = User
        fields = (
            'first_name', 'middle_name', 'last_name',
            'phone_number',
            'house_number', 'road_number', 'postal_code', 'district'
        )
    
    def clean_phone_number(self):
        """Validate phone number format."""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            phone_number = phone_number.replace(' ', '').replace('-', '')
            
            if not phone_number.startswith('01') or len(phone_number) != 11:
                raise forms.ValidationError(
                    'Phone number must be 11 digits starting with 01 (e.g., 01999999999)'
                )
            
            if not phone_number.isdigit():
                raise forms.ValidationError('Phone number must contain only digits')
        
        return phone_number


class UserRegistrationForm(BaseUserCreationForm):
    """Form for user registration with all required fields."""
    
    # Personal Information
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    middle_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Middle Name (Optional)'})
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    
    # Contact Information
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'})
    )
    phone_number = forms.CharField(
        max_length=11,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': '01XXXXXXXXX'}),
        help_text='Enter 11-digit Bangladeshi phone number (e.g., 01999999999)'
    )
    
    # Address Information
    house_number = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'House Number'})
    )
    road_number = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Road Number'})
    )
    postal_code = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Postal Code'})
    )
    district = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'District'})
    )
    
    # Password fields (inherited from UserCreationForm: password1, password2)
    
    class Meta:
        model = User
        fields = (
            'first_name', 'middle_name', 'last_name',
            'email', 'phone_number',
            'house_number', 'road_number', 'postal_code', 'district',
            'password1', 'password2'
        )
    
    def clean_phone_number(self):
        """Validate phone number format."""
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number:
            # Remove any spaces or dashes
            phone_number = phone_number.replace(' ', '').replace('-', '')
            
            # Check if it matches Bangladeshi phone number format
            if not phone_number.startswith('01') or len(phone_number) != 11:
                raise forms.ValidationError(
                    'Phone number must be 11 digits starting with 01 (e.g., 01999999999)'
                )
            
            # Check if it's all digits
            if not phone_number.isdigit():
                raise forms.ValidationError('Phone number must contain only digits')
        
        return phone_number
    
    def clean_email(self):
        """Check if email is already registered."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email address is already registered')
        return email
    
    def save(self, commit=True):
        """Save the user instance."""
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.first_name = self.cleaned_data['first_name']
        user.middle_name = self.cleaned_data.get('middle_name', '')
        user.last_name = self.cleaned_data['last_name']
        user.house_number = self.cleaned_data['house_number']
        user.road_number = self.cleaned_data['road_number']
        user.postal_code = self.cleaned_data['postal_code']
        user.district = self.cleaned_data['district']
        
        if commit:
            user.save()
        return user
