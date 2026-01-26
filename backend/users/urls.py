from django.urls import path
from .views import UserRegisterView, UserLoginView, MeView

urlpatterns = [
    path("register/", UserRegisterView.as_view()),
    path("login/", UserLoginView.as_view()),
    path("me/", MeView.as_view()),
]
