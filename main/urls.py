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
   path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
   path('login/', views.LoginView.as_view(), name='login'),
   path('register/', views.RegisterView.as_view(), name='register'),
   path('', include(router.urls)),
]