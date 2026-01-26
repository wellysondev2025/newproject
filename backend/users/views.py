from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserRegisterSerializer
from .serializers import UserLoginSerializer


class UserRegisterView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Usuário criado com sucesso"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            return Response(
                {
                    "message": "Login realizado com sucesso",
                    "email": user.email,
                    "name": user.name,
                    "is_staff": user.is_staff,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)