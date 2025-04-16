from django.urls import path
from .views import  RegisterView

urlpatterns = [
   path('regiater', RegisterView.as_view(), name="register")
]