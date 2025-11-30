from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from .models import User


class UserCreationForm(forms.ModelForm):
    """Form for creating new users with password confirmation."""
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    
    class Meta:
        model = User
        fields = ('email', 'phone_number', 'first_name', 'middle_name', 'last_name',
                  'house_number', 'road_number', 'postal_code', 'district')
    
    def clean_confirm_password(self):
        """Validate that the two password entries match."""
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")
        return confirm_password
    
    def save(self, commit=True):
        """Save the user with the hashed password."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """Form for updating users."""
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text=(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            "<a href=\"../password/\">this form</a>."
        )
    )
    
    class Meta:
        model = User
        fields = ('email', 'phone_number', 'first_name', 'middle_name', 'last_name',
                  'house_number', 'road_number', 'postal_code', 'district',
                  'is_active', 'is_staff', 'is_superuser')


class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model."""
    form = UserChangeForm
    add_form = UserCreationForm
    
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'district', 
                    'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'district')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'password')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'last_name', 'phone_number')
        }),
        ('Address', {
            'fields': ('house_number', 'road_number', 'postal_code', 'district', 'country')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        ('Authentication', {
            'classes': ('wide',),
            'fields': ('email', 'password', 'confirm_password'),
        }),
        ('Personal Information', {
            'classes': ('wide',),
            'fields': ('first_name', 'middle_name', 'last_name', 'phone_number'),
        }),
        ('Address', {
            'classes': ('wide',),
            'fields': ('house_number', 'road_number', 'postal_code', 'district'),
        }),
        ('Permissions', {
            'classes': ('wide',),
            'fields': ('is_staff', 'is_active'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'country')
    filter_horizontal = ('groups', 'user_permissions')


# Register the User model with the custom admin
admin.site.register(User, UserAdmin)

