from django.urls import path
from . import views

urlpatterns = [
    # API endpoints - Authentication
    path('api/register/', views.register, name='api_register'),
    path('api/login/', views.login, name='api_login'),
    path('api/logout/', views.logout, name='api_logout'),
    path('api/profile/', views.profile, name='api_profile'),
    path('api/refresh/', views.refresh_token, name='api_refresh'),
    
    # API endpoints - Landmarks and Activities
    path('api/landmarks/', views.landmarks_list, name='api_landmarks_list'),
    path('api/landmarks/<str:landmark_id>/', views.landmark_detail, name='api_landmark_detail'),
    path('api/activities/', views.activities_list, name='api_activities_list'),
    path('api/activities/<str:activity_id>/', views.activity_detail, name='api_activity_detail'),
    
    # Template views
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('logout/', views.logout_view, name='logout'),
    
    # Add data views
    path('add-landmark/', views.add_landmark, name='add_landmark'),
    path('add-activity/', views.add_activity, name='add_activity'),
]