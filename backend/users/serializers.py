from rest_framework import serializers
from .models import User, UserProfile
from django.contrib.auth import authenticate
from rest_framework import serializers
from users.services.register_user import RegisterUserService
import re

class UserRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    full_name = serializers.CharField()
    cpf = serializers.CharField()
    birth_date = serializers.DateField()
    address = serializers.CharField()

    # Validação do CPF
    def validate_cpf(self, value):
        if not value:
            raise serializers.ValidationError("CPF é obrigatório.")

        # Remove caracteres não numéricos
        cpf_numbers = re.sub(r'\D', '', value)

        if len(cpf_numbers) != 11:
            raise serializers.ValidationError("CPF deve ter 11 números.")

        if not self.cpf_valido(cpf_numbers):
            raise serializers.ValidationError("CPF inválido.")

        return cpf_numbers

    # Função para checar dígitos verificadores do CPF
    def cpf_valido(self, cpf):
        if cpf in [c*11 for c in "0123456789"]:
            return False  # CPFs com todos os números iguais são inválidos

        def calc_dv(digs):
            s = sum(int(d) * w for d, w in zip(digs, range(len(digs)+1, 1, -1)))
            r = 11 - s % 11
            return '0' if r >= 10 else str(r)

        dv1 = calc_dv(cpf[:9])
        dv2 = calc_dv(cpf[:9] + dv1)
        return cpf[-2:] == dv1 + dv2

    # create continua chamando o service
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
