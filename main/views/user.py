import random
from django.shortcuts import get_object_or_404
from rest_framework import status, mixins, generics, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from main.helpers import StandartPagination
from main.serializers import QuizResultProcessSerializer, CategorySerializer, CourseDetailSerializer, CategoryDetailSerializer, CourseSerializer, GroupSerializer
from main.models import Category, Course, Quiz, Question, Option, Enrollment, QuizResult, TinyMCEImage, Group
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
            'group': user.group.name if user.group else None
        })
        

def quotes(request):
    quotes = [
        { "id": 1, "text": "Stay hungry, stay foolish. – Steve Jobs" },
        { "id": 2, "text": "Dream big. Start small. Act now." },
        { "id": 3, "text": "Do what you love." },
        { "id": 4, "text": "Believe in yourself." },
        { "id": 5, "text": "Work hard, stay humble." },
        { "id": 6, "text": "Failure is growth." },
        { "id": 7, "text": "Keep moving forward." },
        { "id": 8, "text": "No pain, no gain." },
        { "id": 9, "text": "Success is a journey." },
        { "id": 10, "text": "Make today amazing." },
        { "id": 11, "text": "Hustle and heart." },
        { "id": 12, "text": "Live with passion." },
        { "id": 13, "text": "Less talk, more action." },
        { "id": 14, "text": "Dream. Plan. Do." },
        { "id": 15, "text": "Stay positive." },
        { "id": 16, "text": "Create your future." },
        { "id": 17, "text": "The best is yet to come." },
        { "id": 18, "text": "Never give up." },
        { "id": 19, "text": "You can do it!" },
        { "id": 20, "text": "One day at a time." },
        { "id": 21, "text": "Rise and grind." },
        { "id": 22, "text": "Do more, worry less." },
        { "id": 23, "text": "Impossible is nothing." },
        { "id": 24, "text": "Chase your dreams." },
        { "id": 25, "text": "No pressure, no diamonds." },
        { "id": 26, "text": "Progress, not perfection." },
        { "id": 27, "text": "Go the extra mile." },
        { "id": 28, "text": "Live your best life." },
        { "id": 29, "text": "Success loves speed." },
        { "id": 30, "text": "Fear less, do more." },
        { "id": 31, "text": "Make it happen." },
        { "id": 32, "text": "Action cures fear." },
        { "id": 33, "text": "Keep pushing forward." },
        { "id": 34, "text": "Think different. – Apple" },
        { "id": 35, "text": "Happiness is a choice." },
        { "id": 36, "text": "Consistency is key." },
        { "id": 37, "text": "Be a warrior, not a worrier." },
        { "id": 38, "text": "Winners never quit." },
        { "id": 39, "text": "Small steps matter." },
        { "id": 40, "text": "Inhale courage, exhale fear." },
        { "id": 41, "text": "Let it go." },
        { "id": 42, "text": "Your vibe attracts your tribe." },
        { "id": 43, "text": "Less fear, more faith." },
        { "id": 44, "text": "Trust the process." },
        { "id": 45, "text": "Great things take time." },
        { "id": 46, "text": "Love what you do." },
        { "id": 47, "text": "Success starts within." },
        { "id": 48, "text": "Dare to be different." },
        { "id": 49, "text": "Your only limit is you." },
        { "id": 50, "text": "Push harder today." },
        { "id": 51, "text": "Energy flows where focus goes." },
        { "id": 52, "text": "No guts, no glory." },
        { "id": 53, "text": "Find joy in the journey." },
        { "id": 54, "text": "Less ego, more soul." },
        { "id": 55, "text": "Learn, grow, repeat." },
        { "id": 56, "text": "Smile often." },
        { "id": 57, "text": "Life is short. Make it sweet." },
        { "id": 58, "text": "Embrace the struggle." },
        { "id": 59, "text": "Keep it simple." },
        { "id": 60, "text": "Think big." },
        { "id": 61, "text": "Stay strong." },
        { "id": 62, "text": "Done is better than perfect." },
        { "id": 63, "text": "Be the energy you want to attract." },
        { "id": 64, "text": "Speak kindly to yourself." },
        { "id": 65, "text": "Shine bright." },
        { "id": 66, "text": "Learn from yesterday." },
        { "id": 67, "text": "Own your story." },
        { "id": 68, "text": "Turn dreams into reality." },
        { "id": 69, "text": "Follow your intuition." },
        { "id": 70, "text": "Rise by lifting others." },
        { "id": 71, "text": "Enjoy the little things." },
        { "id": 72, "text": "Your time is now." },
        { "id": 73, "text": "Win the morning, win the day." },
        { "id": 74, "text": "Every moment matters." },
        { "id": 75, "text": "Be bold." },
        { "id": 76, "text": "Your future is created today." },
        { "id": 77, "text": "One step at a time." },
        { "id": 78, "text": "Make every second count." },
        { "id": 79, "text": "Take risks, live fully." },
        { "id": 80, "text": "Find your fire." },
        { "id": 81, "text": "Start before you're ready." },
        { "id": 82, "text": "Be a voice, not an echo." },
        { "id": 83, "text": "Live, laugh, love." },
        { "id": 84, "text": "Mindset is everything." },
        { "id": 85, "text": "Stand tall, stay strong." },
        { "id": 86, "text": "Let your light shine." },
        { "id": 87, "text": "Action is magic." },
        { "id": 88, "text": "Lead with love." },
        { "id": 89, "text": "Wake up. Kick ass. Repeat." },
        { "id": 90, "text": "Make yourself proud." },
        { "id": 91, "text": "Live with no regrets." },

        { "id": 92, "text": "Love the process." },
        { "id": 93, "text": "Dare to begin." },
        { "id": 94, "text": "Work hard, stay kind." },
        { "id": 95, "text": "You are enough." },
        { "id": 96, "text": "Take the leap." },
        { "id": 97, "text": "Focus on the good." },
        { "id": 98, "text": "Love yourself first." },
        { "id": 99, "text": "Make waves." },
        { "id": 100, "text": "Stay fearless." },
        { "id": 101, "text": "Nothing is impossible." },
        { "id": 102, "text": "Find your passion." },
        { "id": 103, "text": "You got this!" },
        { "id": 104, "text": "Think happy, be happy." },
        { "id": 105, "text": "Be grateful always." },
        { "id": 106, "text": "Seek progress, not perfection." },
        { "id": 107, "text": "Turn pain into power." },
        { "id": 108, "text": "Create your own sunshine." },
        { "id": 109, "text": "Enjoy every moment." },
        { "id": 110, "text": "Live and let live." },
        { "id": 111, "text": "Write your own story." },
        { "id": 112, "text": "Be fearless in pursuit of your dreams." },
        { "id": 113, "text": "Change the world." },
        { "id": 114, "text": "Push yourself." },
        { "id": 115, "text": "Make history." },
        { "id": 116, "text": "Unleash your potential." },
        { "id": 117, "text": "Focus, hustle, succeed." },
        { "id": 118, "text": "Smile. It's free therapy." },
        { "id": 119, "text": "Enjoy the journey." },
        { "id": 120, "text": "Take charge." },
        { "id": 121, "text": "Success starts now." }
    ]

    return JsonResponse(random.choice(quotes))
        

        
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

class GroupListView(generics.ListAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    pagination_class = None