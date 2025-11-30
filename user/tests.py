from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib.messages import get_messages
from .models import User
from .forms import UserRegistrationForm, UserProfileEditForm


class UserModelTestCase(TestCase):
    """Test cases for the User model."""
    
    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'email': 'test@example.com',
            'phone_number': '01712345678',
            'first_name': 'John',
            'last_name': 'Doe',
            'house_number': '123',
            'road_number': '45',
            'postal_code': '1234',
            'district': 'Dhaka',
            'password': 'testpass123'
        }
    
    def test_create_user(self):
        """Test creating a regular user."""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.phone_number, '01712345678')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.last_name, 'Doe')
        self.assertEqual(user.country, 'Bangladesh')
        self.assertTrue(user.check_password('testpass123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = User.objects.create_superuser(**self.user_data)
        
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
    
    def test_user_full_name(self):
        """Test getting user's full name."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), 'John Doe')
        
        # Test with middle name
        user.middle_name = 'Middle'
        self.assertEqual(user.get_full_name(), 'John Middle Doe')
    
    def test_user_short_name(self):
        """Test getting user's short name."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), 'John')
    
    def test_user_full_address(self):
        """Test getting user's full address."""
        user = User.objects.create_user(**self.user_data)
        expected_address = "House: 123, Road: 45, Postal Code: 1234, Dhaka, Bangladesh"
        self.assertEqual(user.get_full_address(), expected_address)
    
    def test_email_required(self):
        """Test that email is required."""
        data = self.user_data.copy()
        data['email'] = ''
        
        with self.assertRaises(ValueError):
            User.objects.create_user(**data)
    
    def test_phone_number_required(self):
        """Test that phone number is required."""
        data = self.user_data.copy()
        data['phone_number'] = ''
        
        with self.assertRaises(ValueError):
            User.objects.create_user(**data)
    
    def test_email_unique(self):
        """Test that email must be unique."""
        User.objects.create_user(**self.user_data)
        
        # Try to create another user with the same email
        data = self.user_data.copy()
        data['phone_number'] = '01812345678'  # Different phone
        
        with self.assertRaises(Exception):
            User.objects.create_user(**data)
    
    def test_phone_number_validation(self):
        """Test phone number validation."""
        # Invalid: Less than 11 digits
        data = self.user_data.copy()
        data['phone_number'] = '0171234567'
        data['email'] = 'test2@example.com'
        user = User(**data)
        
        with self.assertRaises(ValidationError):
            user.full_clean()
        
        # Invalid: Doesn't start with 01
        data['phone_number'] = '12345678901'
        data['email'] = 'test3@example.com'
        user = User(**data)
        
        with self.assertRaises(ValidationError):
            user.full_clean()
        
        # Invalid: Contains non-digits
        data['phone_number'] = '0171234567a'
        data['email'] = 'test4@example.com'
        user = User(**data)
        
        with self.assertRaises(ValidationError):
            user.full_clean()
    
    def test_country_default(self):
        """Test that country defaults to Bangladesh."""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.country, 'Bangladesh')
    
    def test_user_str_representation(self):
        """Test string representation of user."""
        user = User.objects.create_user(**self.user_data)
        expected = f"John Doe (test@example.com)"
        self.assertEqual(str(user), expected)


class UserRegistrationFormTestCase(TestCase):
    """Test cases for the UserRegistrationForm."""
    
    def setUp(self):
        """Set up test data."""
        self.valid_data = {
            'first_name': 'John',
            'middle_name': '',
            'last_name': 'Doe',
            'email': 'newuser@example.com',
            'phone_number': '01712345678',
            'house_number': '123',
            'road_number': '45',
            'postal_code': '1234',
            'district': 'Dhaka',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
    
    def test_valid_form(self):
        """Test form with valid data."""
        form = UserRegistrationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
    
    def test_phone_number_validation_invalid_length(self):
        """Test phone number with invalid length."""
        data = self.valid_data.copy()
        data['phone_number'] = '0171234567'  # 10 digits
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
    
    def test_phone_number_validation_invalid_prefix(self):
        """Test phone number not starting with 01."""
        data = self.valid_data.copy()
        data['phone_number'] = '12345678901'
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
    
    def test_phone_number_validation_non_digits(self):
        """Test phone number with non-digit characters."""
        data = self.valid_data.copy()
        data['phone_number'] = '0171234567a'
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
    
    def test_duplicate_email(self):
        """Test form rejects duplicate email."""
        User.objects.create_user(
            email='existing@example.com',
            phone_number='01712345678',
            first_name='Existing',
            last_name='User',
            house_number='1',
            road_number='1',
            postal_code='1000',
            district='Dhaka',
            password='pass123'
        )
        data = self.valid_data.copy()
        data['email'] = 'existing@example.com'
        data['phone_number'] = '01812345678'  # Different phone
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_password_mismatch(self):
        """Test form rejects mismatched passwords."""
        data = self.valid_data.copy()
        data['password2'] = 'DifferentPass123!'
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_form_saves_user(self):
        """Test form correctly saves user."""
        form = UserRegistrationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertEqual(user.first_name, 'John')
        self.assertEqual(user.phone_number, '01712345678')
        self.assertTrue(user.check_password('ComplexPass123!'))


class UserProfileEditFormTestCase(TestCase):
    """Test cases for the UserProfileEditForm."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@example.com',
            phone_number='01712345678',
            first_name='John',
            last_name='Doe',
            house_number='123',
            road_number='45',
            postal_code='1234',
            district='Dhaka',
            password='testpass123'
        )
    
    def test_form_excludes_email(self):
        """Test that email field is not in form."""
        form = UserProfileEditForm(instance=self.user)
        self.assertNotIn('email', form.fields)
    
    def test_valid_profile_update(self):
        """Test updating profile with valid data."""
        data = {
            'first_name': 'Jane',
            'middle_name': 'Marie',
            'last_name': 'Smith',
            'phone_number': '01812345678',
            'house_number': '456',
            'road_number': '78',
            'postal_code': '5678',
            'district': 'Chittagong'
        }
        form = UserProfileEditForm(data=data, instance=self.user)
        self.assertTrue(form.is_valid())
        updated_user = form.save()
        self.assertEqual(updated_user.first_name, 'Jane')
        self.assertEqual(updated_user.middle_name, 'Marie')
        self.assertEqual(updated_user.phone_number, '01812345678')
    
    def test_invalid_phone_number(self):
        """Test form rejects invalid phone number."""
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'phone_number': '123',  # Invalid
            'house_number': '123',
            'road_number': '45',
            'postal_code': '1234',
            'district': 'Dhaka'
        }
        form = UserProfileEditForm(data=data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)


class RegisterViewTestCase(TestCase):
    """Test cases for the register view."""
    
    def setUp(self):
        """Set up test client."""
        self.client = Client()
        self.register_url = reverse('user:register')
    
    def test_register_page_loads(self):
        """Test register page loads successfully."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/register.html')
        self.assertIsInstance(response.context['form'], UserRegistrationForm)
    
    def test_successful_registration(self):
        """Test successful user registration."""
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'testuser@example.com',
            'phone_number': '01712345678',
            'house_number': '123',
            'road_number': '45',
            'postal_code': '1234',
            'district': 'Dhaka',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, reverse('user:login'))
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())
    
    def test_registration_with_invalid_data(self):
        """Test registration with invalid data."""
        data = {
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'invalid-email',  # Invalid email
            'phone_number': '123',  # Invalid phone
            'password1': 'pass',
            'password2': 'different'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='invalid-email').exists())
    
    def test_authenticated_user_redirect(self):
        """Test authenticated user is redirected from register page."""
        user = User.objects.create_user(
            email='existing@example.com',
            phone_number='01712345678',
            first_name='Existing',
            last_name='User',
            house_number='1',
            road_number='1',
            postal_code='1000',
            district='Dhaka',
            password='pass123'
        )
        self.client.login(email='existing@example.com', password='pass123')
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user:profile'))


class LoginViewTestCase(TestCase):
    """Test cases for the login view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.login_url = reverse('user:login')
        self.user = User.objects.create_user(
            email='test@example.com',
            phone_number='01712345678',
            first_name='John',
            last_name='Doe',
            house_number='123',
            road_number='45',
            postal_code='1234',
            district='Dhaka',
            password='testpass123'
        )
    
    def test_login_page_loads(self):
        """Test login page loads successfully."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/login.html')
    
    def test_successful_login(self):
        """Test successful login."""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user:profile'))
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials."""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any('Invalid email or password' in str(m) for m in messages))
    
    def test_authenticated_user_redirect(self):
        """Test authenticated user is redirected from login page."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user:profile'))


class LogoutViewTestCase(TestCase):
    """Test cases for the logout view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.logout_url = reverse('user:logout')
        self.user = User.objects.create_user(
            email='test@example.com',
            phone_number='01712345678',
            first_name='John',
            last_name='Doe',
            house_number='123',
            road_number='45',
            postal_code='1234',
            district='Dhaka',
            password='testpass123'
        )
    
    def test_logout_requires_authentication(self):
        """Test logout requires authentication."""
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        # Should redirect to login
    
    def test_successful_logout(self):
        """Test successful logout."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user:login'))


class ProfileViewTestCase(TestCase):
    """Test cases for the profile view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.profile_url = reverse('user:profile')
        self.user = User.objects.create_user(
            email='test@example.com',
            phone_number='01712345678',
            first_name='John',
            last_name='Doe',
            house_number='123',
            road_number='45',
            postal_code='1234',
            district='Dhaka',
            password='testpass123'
        )
    
    def test_profile_requires_authentication(self):
        """Test profile page requires authentication."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 302)
    
    def test_profile_page_loads(self):
        """Test profile page loads for authenticated user."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/profile.html')
        self.assertEqual(response.context['user'], self.user)


class EditProfileViewTestCase(TestCase):
    """Test cases for the edit profile view."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.edit_profile_url = reverse('user:edit_profile')
        self.user = User.objects.create_user(
            email='test@example.com',
            phone_number='01712345678',
            first_name='John',
            last_name='Doe',
            house_number='123',
            road_number='45',
            postal_code='1234',
            district='Dhaka',
            password='testpass123'
        )
    
    def test_edit_profile_requires_authentication(self):
        """Test edit profile requires authentication."""
        response = self.client.get(self.edit_profile_url)
        self.assertEqual(response.status_code, 302)
    
    def test_edit_profile_page_loads(self):
        """Test edit profile page loads for authenticated user."""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(self.edit_profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user/edit_profile.html')
        self.assertIsInstance(response.context['form'], UserProfileEditForm)
    
    def test_successful_profile_update(self):
        """Test successful profile update."""
        self.client.login(email='test@example.com', password='testpass123')
        data = {
            'first_name': 'Jane',
            'middle_name': 'Marie',
            'last_name': 'Smith',
            'phone_number': '01812345678',
            'house_number': '456',
            'road_number': '78',
            'postal_code': '5678',
            'district': 'Chittagong'
        }
        response = self.client.post(self.edit_profile_url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user:profile'))
        
        # Verify changes
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Jane')
        self.assertEqual(self.user.phone_number, '01812345678')
    
    def test_profile_update_with_invalid_data(self):
        """Test profile update with invalid data."""
        self.client.login(email='test@example.com', password='testpass123')
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'phone_number': '123',  # Invalid
            'house_number': '456',
            'road_number': '78',
            'postal_code': '5678',
            'district': 'Chittagong'
        }
        response = self.client.post(self.edit_profile_url, data)
        self.assertEqual(response.status_code, 200)  # Should return to form
        
        # Verify no changes
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')  # Unchanged

