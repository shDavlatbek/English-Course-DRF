from django.shortcuts import get_object_or_404
from rest_framework import status, mixins, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from main.helpers import StandartPagination
from main.serializers import QuizResultProcessSerializer, CategorySerializer, CourseDetailSerializer, CategoryDetailSerializer, CourseSerializer
from main.models import Category, Course, Quiz, Question, Option, Enrollment, QuizResult, TinyMCEImage
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from urllib.parse import urljoin


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
        serializer = CourseSerializer(courses, context={'request': request},  many=True)
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
        
        
        
@csrf_exempt  # Note: For production, consider a more secure approach for CSRF
@login_required  # Optional: Restrict uploads to authenticated users
@swagger_auto_schema(schema=None, auto_schema=None)
def upload_image(request):
    """Handle image uploads from TinyMCE editor."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file uploaded'}, status=400)
    
    uploaded_file = request.FILES['file']
    
    # Check if file is an image
    if not uploaded_file.content_type.startswith('image/'):
        return JsonResponse({'error': 'File is not an image'}, status=400)
    
    # Create a new image record
    image = TinyMCEImage(title=uploaded_file.name)
    image.image = uploaded_file
    image.save()
    
    # Get the absolute URL by combining the site URL with the media URL
    site_url = request.build_absolute_uri('/').rstrip('/')
    relative_url = image.image.url
    
    # Ensure we have an absolute URL
    if relative_url.startswith('/'):
        # Already a root-relative URL, just add the site domain
        absolute_url = f"{site_url}{relative_url}"
    else:
        # Combine with the site URL
        absolute_url = urljoin(site_url, relative_url)
    
    # Return the absolute URL to the image
    return JsonResponse({
        'location': absolute_url,  # Absolute URL for TinyMCE
        'success': True
    })