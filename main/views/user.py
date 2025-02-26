from django.shortcuts import get_object_or_404
from rest_framework import status, mixins, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from main.helpers import StandartPagination
from main.serializers import QuizResultProcessSerializer, CategorySerializer, CourseDetailSerializer, CategoryDetailSerializer, CourseSerializer
from main.models import Category, Course, Quiz, Question, Option, Enrollment, QuizResult
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class UserView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
      manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT token for authentication",
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer '
            )
        ],
        responses={
            200: openapi.Response(
                description="List of courses enrolled by the authenticated user",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Course ID"),
                            'title': openapi.Schema(type=openapi.TYPE_STRING, description="Course title"),
                            'slug': openapi.Schema(type=openapi.TYPE_STRING, description="Course slug"),
                            'category': openapi.Schema(type=openapi.TYPE_STRING, description="Course category"),
                            'level': openapi.Schema(type=openapi.TYPE_STRING, description="Course level"),
                            'description': openapi.Schema(type=openapi.TYPE_STRING, description="Course description"),
                            'content': openapi.Schema(type=openapi.TYPE_STRING, description="Course content"),
                        }
                    )
                )
            ),
            401: openapi.Response(
                description="Unauthorized: User is not authenticated"
            )
        }
    )
    def get(self, request):
        user = request.user
        enrolled_courses = Enrollment.objects.filter(user=user).values_list('course', flat=True)
        courses = Course.objects.filter(id__in=enrolled_courses)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    


class UserMeView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT token for authentication",
                type=openapi.TYPE_STRING,
                required=True,
                default='Bearer '
            )
        ],
        responses={
            200: openapi.Response(
                description="Details of the authenticated user",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'id': openapi.Schema(type=openapi.TYPE_INTEGER, description="User ID"),
                        'username': openapi.Schema(type=openapi.TYPE_STRING, description="Username"),
                        'email': openapi.Schema(type=openapi.TYPE_STRING, description="Email"),
                        'first_name': openapi.Schema(type=openapi.TYPE_STRING, description="First name"),
                        'last_name': openapi.Schema(type=openapi.TYPE_STRING, description="Last name"),
                    }
                )
            ),
            401: openapi.Response(
                description="Unauthorized: User is not authenticated"
            )
        }
    )
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        })