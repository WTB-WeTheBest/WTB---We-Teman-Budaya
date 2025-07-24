from django.urls import path
from . import views

urlpatterns = [
    # API endpoints
    path('api/register/', views.register, name='api_register'),
    path('api/login/', views.login, name='api_login'),
    path('api/logout/', views.logout, name='api_logout'),
    path('api/profile/', views.profile, name='api_profile'),
    path('api/refresh/', views.refresh_token, name='api_refresh'),
    
    # Template views
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('logout/', views.logout_view, name='logout'),
]