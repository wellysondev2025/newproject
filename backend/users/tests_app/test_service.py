from django.test import TestCase
from django.core import mail
from users.services.register_user import RegisterUserService
from users.models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterUserServiceTest(TestCase):

    def test_register_user_creates_user_and_profile_and_sends_email(self):
        # Dados de teste
        data = {
            "email": "teste@example.com",
            "password": "senha123",
            "full_name": "Fulano Teste",
            "cpf": "",
            "birth_date": "2000-01-01",
            "address": "Rua Teste, 123"
        }

        # Executa o service
        user = RegisterUserService.execute(data)

        # Verifica se usuário foi criado
        self.assertTrue(User.objects.filter(email="teste@example.com").exists())

        # Verifica se profile foi criado
        profile = UserProfile.objects.get(user=user)
        self.assertEqual(profile.full_name, "Fulano Teste")

        # Verifica se email foi enviado
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Ative sua conta", mail.outbox[0].subject)
        self.assertIn(user.email, mail.outbox[0].to)
