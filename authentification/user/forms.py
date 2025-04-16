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

 