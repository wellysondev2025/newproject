from typing import Any
from django.db import transaction
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from urllib.parse import quote
from django.core.mail import send_mail
from django.conf import settings

from users.models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterUserService:

    @staticmethod
    @transaction.atomic
    def execute(validated_data: dict) -> Any:  # <- tipo seguro e sem amarelo
        # Remove a senha do dict
        password = validated_data.pop("password")

        # Dados extras do profile
        profile_data = {
            "full_name": validated_data.pop("full_name"),
            "cpf": validated_data.pop("cpf"),
            "birth_date": validated_data.pop("birth_date"),
            "address": validated_data.pop("address"),
        }

        # Cria o usuário
        user = User.objects.create_user(
            password=password,
            is_active=False,
            **validated_data
        )

        # Cria o profile
        UserProfile.objects.create(user=user, **profile_data)

        # Gera UID e token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Monta link de ativação
        activation_link = f"http://localhost:8000/api/v1/users/activate/{uid}/{quote(token)}/"

        # Envia email
        send_mail(
            subject="Ative sua conta",
            message=f"Ative sua conta clicando no link abaixo:\n\n{activation_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return user
