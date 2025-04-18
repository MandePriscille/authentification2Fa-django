from django.urls import path
from .views import  RegisterView, LoginView, verifyEmailView, HomeView

urlpatterns = [
   path('register/', RegisterView.as_view(), name="register"),
   path('verififyEmail/', verifyEmailView.as_view(), name="verififyEmail"),
   path('login/', LoginView.as_view(), name="login"),
   path('home/', HomeView.as_view(), name="home")
]