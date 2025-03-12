from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework import generics

import main.serializers as serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class LoginView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=serializers.LoginSerializer,
        responses={
            200: openapi.Response(
                description="Login successful, token returned",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'token': openapi.Schema(type=openapi.TYPE_STRING, description="JWT token"),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Success status")
                    }
                )
            ),
            400: openapi.Response(
                description="Invalid credentials or missing fields"
            )
        }
    )
    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = AccessToken.for_user(user)
            return Response(
                {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name
                    },
                    "success": True,
                    "token": str(refresh)
                },
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "success": False,
                "detail": serializer.errors
            }, 
            status=status.HTTP_400_BAD_REQUEST
        )



class RegisterView(generics.CreateAPIView):
    serializer_class = serializers.RegisterSerializer

    @swagger_auto_schema(
        operation_description="Register a new user",
        request_body=serializers.RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully",
                schema=serializers.RegisterSerializer
            ),
            400: openapi.Response(
                description="Bad Request: Invalid input data"
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            {
                "user": serializers.RegisterSerializer(user, context=self.get_serializer_context()).data,
                "message": "User Created Successfully.  Now perform Login to get your token",
            }
        )