from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken

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



class RegisterView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=serializers.RegisterSerializer,
        responses={
            201: openapi.Response(
                description="User registered successfully and JWT token generated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="User ID"),
                                'email': openapi.Schema(type=openapi.TYPE_STRING, description="User email"),
                                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="User first name"),
                                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="User last name"),
                            }
                        ),
                        'token': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="JWT token"
                        ),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Success status")
                    },
                    required=['user', 'token']
                )
            ),
            400: openapi.Response(
                description="Bad Request: Invalid input data"
            )
        }
    )
    def post(self, request):
        serializer = serializers.RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate refresh token for the created user
            refresh = AccessToken.for_user(user)
            return Response(
                {
                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name
                    },
                    "token": str(refresh),
                    "success": True
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)