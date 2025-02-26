from django.urls import include, path
from main import views
from rest_framework import routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="API Documentation",
      default_version='v1',
      description="API documentation for your project",
   ),
   public=True,
)

router = routers.DefaultRouter()

urlpatterns = [
   path('upload-image/', views.upload_image, name='upload_image'),
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('login/', views.LoginView.as_view(), name='login'),
   path('register/', views.RegisterView.as_view(), name='register'),
   path('user/', views.UserView.as_view(), name='user'),
   path('user/me/', views.UserMeView.as_view(), name='user'),
   path('category/', views.CourseCategoryView.as_view(), name='course-category'),
   path('category/<slug:slug>/', views.CourseCategoryDetailView.as_view(), name='course-category-detail'),
   path('enroll/<slug:slug>/', views.EnrollmentView.as_view(), name='enroll-course'),
   path('course/', views.CourseView.as_view(), name='course-list'),
   path('course/<slug:slug>/', views.CourseDetailView.as_view(), name='course-detail'),
   path('course/<slug:slug>/submit-quiz', views.ProcessQuizResultView.as_view(), name='submit-quiz'),
   path('', include(router.urls)),
]