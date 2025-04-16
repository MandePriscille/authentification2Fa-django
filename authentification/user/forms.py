from  django import forms
from .models import User, Otp

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label = "Password",
        widget = forms.PasswordInput
    )
    confirm_password = forms.CharField(
        label = "Confirm Password",
        widget = forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password']

    # clean method verifies that the password and confirm_password fields match
    # clean method also verifies that the email address doesn't already exist
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', 'Passwords do not match')

        # verify the email address don't already exist
        email = cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude():
            self.add_error('email', 'Email already exists')
        return cleaned_data
    

class OtpForm(forms.ModelForm):
    class Meta:
        model = Otp
        fields = ['code']

 
class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if not email or not password:
            self.add_error('email', 'This field is required')
            self.add_error('password', 'This field is required')
            return cleaned_data

        user = User.objects.get(email=email)
        if not user.is_active:
            self.add_error('email', 'Your account is not activated. Please check your email for the verification code.')
            return cleaned_data
        
        if not user.check_password(password):
            self.add_error('password', 'Invalid password')
            return cleaned_data
        return cleaned_data