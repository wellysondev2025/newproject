from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import User
from .serializers import UserRegisterSerializer
from .serializers import UserLoginSerializer
from .serializers import UserProfileSerializer
from .serializers import UserProfileUpdateSerializer
from .serializers import ChangePasswordSerializer
from .serializers import ResendActivationSerializer
from .serializers import AdminUserListSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.responses import success_response, error_response
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from urllib.parse import unquote
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from urllib.parse import quote
from django.core.mail import send_mail
from django.conf import settings




def decode_uid(uidb64):
    uidb64 += "=" * (-len(uidb64) % 4)  # corrige o padding
    return force_str(urlsafe_base64_decode(uidb64))

# Registrar usuario
class UserRegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data={"message": "Usuário criado com sucesso"},
                status=201
            )
        return error_response(serializer.errors, status=400)


# Logar no sistema
class UserLoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            return success_response(
                data={
                    "email": user.email,
                    "name": user.profile.full_name,
                    "is_staff": user.is_staff,
                }
            )
        return error_response(serializer.errors, status=400)


# Class que referencia ao proprio USUARIO.
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = getattr(request.user, "profile", None)
        if not profile:
            return error_response(
                {"error": "Perfil não encontrado"},
                status=404
            )
        profile_data = UserProfileSerializer(profile).data

        return success_response(
            data={
                "email": request.user.email,
                "profile": profile_data
            }
        )


class AdminOnlyView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = AdminUserListSerializer(users, many=True)
        return success_response(data=serializer.data)

class UserUpdateView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def put(self, request):
        profile = getattr(request.user, "profile", None)

        if not profile:
            return error_response({"error": "Perfil não encontrado"}, status=404)

        serializer = UserProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return success_response(
                data={"message": "Perfil atualizado com sucesso"}
            )

        return error_response(serializer.errors, status=400)


class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            # Verifica senha atual
            if not user.check_password(serializer.validated_data["current_password"]):
                return error_response({"error": "Senha atual incorreta"}, status=400)

            # Atualiza senha
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            return success_response({"message": "Senha atualizada com sucesso"})

        return error_response(serializer.errors, status=400)
    

class ActivateUserView(APIView):
    permission_classes = []

    def get(self, request, uidb64, token):
        token = unquote(token).replace("\n", "").replace("\r", "")

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except Exception:
            return error_response({"error": "Link inválido"}, status=400)

        if not default_token_generator.check_token(user, token):
            return error_response({"error": "Link inválido ou expirado"}, status=400)

        user.is_active = True
        user.save()

        return success_response({"message": "Conta ativada com sucesso"})


class ResendActivationView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = ResendActivationSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(serializer.errors, status=400)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return error_response({"error": "Usuário não encontrado"}, status=404)

        if user.is_active:
            return error_response({"error": "Usuário já está ativo"}, status=400)

        # gerar novo token e uid
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        activation_link = f"http://localhost:8000/api/v1/users/activate/{uid}/{quote(token)}/"

        # enviar email
        send_mail(
            subject="Reenvio: Ative sua conta",
            message=f"Ative sua conta: {activation_link}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )

        return success_response({"activation_link": activation_link})
