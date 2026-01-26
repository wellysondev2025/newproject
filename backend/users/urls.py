from django.urls import path
from .views import UserRegisterView, UserLoginView, MeView, AdminOnlyView

urlpatterns = [
    path("register/", UserRegisterView.as_view()),
    path("login/", UserLoginView.as_view()),
    path("me/", MeView.as_view()),
    path("admin-test/", AdminOnlyView.as_view()),
]
