import random
import string
from datetime import timedelta
from django.utils import timezone
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.views import View
from .models import Otp, User

# from authentification.user.forms import RegisterForm, OtpForm
from .forms import RegisterForm, OtpForm, LoginForm


class RegisterView(View):
    template_name = 'accounts/register.html'
    form_class = RegisterForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                is_active=False
            )
        
            # Genere code OTP
            otp_code = str(random.randint(1000, 9999))
            exppiration = timezone.now() + timedelta(minutes=5)

            # create OTP
            Otp.objects.update_or_create(
                user=user,
                defaults={
                    'code': otp_code,
                    'expiration_at': exppiration,
                    'is_used': False
                }
            )

            # sent mail
            send_mail(
                subject='Your verification code : {otp_code}',
                message='Your code is: {}'.format(otp_code),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )

            request.session['register_email'] = user.email
            messages.success(request, 'Your account has been created. Please check your email for the verification code.')
            return redirect(reverse_lazy('verififyEmail'))
        return render(request, self.template_name, {'form': form})      
    

class verifyEmailView(View):
    template_name = 'accounts/verify_email.html'
    forms_class = OtpForm

    def get(self, request):
        if 'register_email' not in request.session:
            messages.error(request, 'pleace register first')
            return redirect('register')
        
        form = self.forms_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        if 'register_email' not in request.session:
            return redirect('register')
        
        form = self.forms_class(request.POST)
        email = request.session['register_email']
        if form.is_valid():
            otp_code = form.cleaned_data['code']

            try:
                user = User.objects.get(email=email)
                otp = Otp.objects.get(user=user, code=otp_code)

                if otp.is_used:
                    messages.error(request, 'This code has been used. Please try again.')
                elif not otp.is_valid():
                    messages.error(request, 'This code is not valid. Please try again.')
                else:
                    user.is_active = True
                    otp.save()
                    user.is_active = True
                    user.save()
                    del request.session['register_email']
                    messages.success(request, 'Your account has been activated. Please login.')
                    return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'This email is not registered. Please try again.')
            except Otp.DoesNotExist:
                messages.error(request, 'incorrect otp. Please try again.')
        return redirect('register')


class LoginView(View):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user = authenticate(request,email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'You have been logged in.')
                return redirect('home')
            else:
                messages.success(request, 'You have been logged in.')
                return redirect('home')
        else:
            messages.error(request, 'Your account is not activated. Please check your email for the verification code.')
        return render(request, self.template_name, {'form': form})
    

class HomeView(View):
    template_name = 'accounts/home.html'

    def get(self, request):
        return render(request, self.template_name)