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




class ProcessQuizResultView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Process a quiz result and return the score and correct answers.",
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
        request_body=QuizResultProcessSerializer,
        responses={
            201: openapi.Response(
                description="Quiz result processed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'quiz_result_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Quiz result ID"),
                        'score': openapi.Schema(type=openapi.TYPE_INTEGER, description="Score obtained in the quiz"),
                        'correct_answers': openapi.Schema(type=openapi.TYPE_INTEGER, description="Number of correct answers")
                    }
                )
            ),
            400: openapi.Response(
                description="Bad Request: Invalid input data"
            )
        }
    )
    def post(self, request, *args, **kwargs):
        serializer = QuizResultProcessSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            quiz_result = serializer.save()
            return Response(
                {
                    'quiz_result_id': quiz_result.id, 
                    'score': quiz_result.score,
                    'correct_answers': quiz_result.correct_answers
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
class CourseCategoryView(generics.ListAPIView):
    """
    Retrieve a list of all Course instances
    """
    pagination_class = None
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = [AllowAny]


class CourseCategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryDetailSerializer
    lookup_field = 'slug'
    
    @swagger_auto_schema(
        operation_description="Retrieve detailed information about a course category, including its courses. Optionally, filter the courses by a 'level' query parameter (e.g., ?level=a1).",
        manual_parameters=[
            openapi.Parameter(
                'level',
                openapi.IN_QUERY,
                description="Filter courses by level (e.g., a1)",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class CourseView(generics.ListAPIView):
    """
    Retrieve a list of all Course instances
    """
    pagination_class = StandartPagination
    serializer_class = CourseSerializer
    queryset = Course.objects.all()
    permission_classes = [AllowAny]



class EnrollmentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT token for authentication",
                type=openapi.TYPE_STRING,
                default='Bearer '
            ),
            openapi.Parameter(
                'slug',
                openapi.IN_PATH,
                description="Course slug",
                type=openapi.TYPE_STRING
            )
        ],
        operation_description="Enroll in a course. If the user is already enrolled, return a message indicating that.",
        responses={
            201: openapi.Response(
                description="Enrollment successful",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Enrollment message"),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Success status")
                    }
                )
            ),
            200: openapi.Response(
                description="Already enrolled",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING, description="Enrollment message"),
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Success status")
                    }
                )
            )
        }
    )
    def post(self, request, slug):
        course = get_object_or_404(Course, slug=slug)
        enrollment, created = Enrollment.objects.get_or_create(
            user=request.user, course=course)
        if created:
            return Response(
                {
                    "message": "Enrollment successful",
                    "success": True,
                }, 
                status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "Already enrolled",
                "success": False
                }, status=status.HTTP_200_OK)

    

class CourseDetailView(generics.RetrieveAPIView):
    """
    Retrieve a single Course instance by its slug, with related quizzes, questions, options, and results.
    """
    # Define the queryset with prefetch_related for performance optimization
    queryset = Course.objects.prefetch_related(
        'quizzes__questions__options', 'quizzes__results'
    )
    
    # Set the lookup field to 'slug' (instead of the default 'pk')
    lookup_field = 'slug'
    
    # Specify the serializer class to use
    serializer_class = CourseDetailSerializer
    
    # Optional: Explicitly allow any user to access this view (matches original behavior)
    permission_classes = [AllowAny]
    @swagger_auto_schema(    
        operation_description="Retrieve detailed information about a course, including its quizzes, questions, options, and results.",
        manual_parameters=[
            openapi.Parameter(
                'slug',
                openapi.IN_PATH,
                description="Course slug",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'Authorization',
                openapi.IN_HEADER,
                description="JWT token for authentication",
                type=openapi.TYPE_STRING,
                default='Bearer '
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)