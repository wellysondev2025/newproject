from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import IsAuthenticated
from .serializers import UserRegisterSerializer
from .serializers import UserLoginSerializer

from utils.responses import success_response, error_response



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

class UserLoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            return success_response(
                data={
                    "email": user.email,
                    "name": user.name,
                    "is_staff": user.is_staff,
                }
            )
        return error_response(serializer.errors, status=400)



class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return success_response(
            data={
                "email": request.user.email,
                "name": request.user.name,
            }
        )   
