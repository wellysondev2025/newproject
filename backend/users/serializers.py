from rest_framework import serializers
from .models import User, UserProfile
from django.contrib.auth import authenticate
from rest_framework import serializers
from users.services.register_user import RegisterUserService
import re
from ..utils import validar_cpf

class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    full_name = serializers.CharField()
    cpf = serializers.CharField()
    birth_date = serializers.DateField()
    address = serializers.CharField()

    # Validação do CPF chamando a função utilitária
    def validate_cpf(self, value):
        try:
            return validar_cpf(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))

    def create(self, validated_data):
        return RegisterUserService.execute(validated_data)



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
