from rest_framework import serializers
from .models import User, UserProfile
from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from urllib.parse import quote


class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    full_name = serializers.CharField()
    cpf = serializers.CharField()
    birth_date = serializers.DateField()
    address = serializers.CharField()

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password")

        profile_data = {
            "full_name": validated_data.pop("full_name"),
            "cpf": validated_data.pop("cpf"),
            "birth_date": validated_data.pop("birth_date"),
            "address": validated_data.pop("address"),
        }

        user = User.objects.create_user(
            password=password,
            is_active = False,
            **validated_data
        )

        UserProfile.objects.create(
            user=user,
            **profile_data
        )

        # gera token e uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # cria link de ativação
        activation_link = f"http://localhost:8000/api/v1/users/activate/{uid}/{quote(token)}/"

        message = f"Ative sua conta clicando no link abaixo:\n\n{activation_link}"
        send_mail(
            subject="Ative sua conta",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(
            email=data["email"],
            password=data["password"]
        )

        if not user:
            raise serializers.ValidationError("Credenciais inválidas")

        if not user.is_active:
            raise serializers.ValidationError("Usuário inativo")

        data["user"] = user
        return data



class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "full_name",
            "cpf",
            "birth_date",
            "address",
        )

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("full_name", "address")



class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data["new_password"] != data["new_password_confirm"]:
            raise serializers.ValidationError("As senhas não coincidem.")
        return data

class ResendActivationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class AdminUserListSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "is_active",
            "is_staff",
            "created_at",
            "profile",
        )
