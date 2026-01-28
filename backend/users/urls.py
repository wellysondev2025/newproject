from django.urls import path
from .views import UserRegisterView, UserLoginView, MeView, AdminOnlyView, UserUpdateView, ChangePasswordView, ActivateUserView, ResendActivationView

urlpatterns = [
    path("register/", UserRegisterView.as_view()),
    path("login/", UserLoginView.as_view()),
    path("me/", MeView.as_view()),
    path("admin-test/", AdminOnlyView.as_view()),
    path("me/update/", UserUpdateView.as_view()),
    path("me/change-password/", ChangePasswordView.as_view()),
    path("activate/<uidb64>/<token>/", ActivateUserView.as_view()),
    path("resend-activation/", ResendActivationView.as_view()),
]
