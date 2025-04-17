from  django import forms
from .models import User, Otp
from django.core.validators import MinLengthValidator

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Créez un mot de passe sécurisé',
            'autocomplete': 'new-password',
        }),
        validators=[MinLengthValidator(8)],
        help_text="Minimum 8 caractères"
    )
    
    confirm_password = forms.CharField(
        label="Confirmation du mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Retapez votre mot de passe',
            'autocomplete': 'new-password',
        })
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre prénom',
                'autofocus': True
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Votre nom'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'exemple@email.com'
            }),
        }
        labels = {
            'first_name': "Prénom",
            'last_name': "Nom",
            'email': "Adresse email",
        }
        help_texts = {
            'email': "we not share your email with anyone else",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs.update({'class': 'form-control'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "This email is already registered.",
                "pleace register first",
            )
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error(
                'confirm_password',
                forms.ValidationError(
                    "Les mots de passe ne correspondent pas",
                    code='password_mismatch'
                )
            )        
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
       

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