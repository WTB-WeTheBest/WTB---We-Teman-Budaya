from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib import messages
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    LandmarkSerializer, ActivitySerializer
)
from orm_center.models import Landmark, Activity, Marker, Location, Picture
from .forms import CombinedLandmarkForm, CombinedActivityForm
import uuid
from django.db import transaction


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'User created successfully',
            'user': UserProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'user': UserProfileSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        return Response({
            'access': str(token.access_token),
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)


# Landmark and Activity API endpoints
@api_view(['GET'])
@permission_classes([AllowAny])
def landmarks_list(request):
    """Get all landmarks"""
    try:
        landmarks = Landmark.objects.select_related('id__id_location').prefetch_related('id__picture_set').all()
        serializer = LandmarkSerializer(landmarks, many=True)
        return Response({
            'landmarks': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def landmark_detail(request, landmark_id):
    """Get a specific landmark by ID"""
    try:
        landmark = Landmark.objects.select_related('id__id_location').prefetch_related('id__picture_set').get(id=landmark_id)
        serializer = LandmarkSerializer(landmark)
        return Response({
            'landmark': serializer.data
        }, status=status.HTTP_200_OK)
    except Landmark.DoesNotExist:
        return Response({'error': 'Landmark not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def activities_list(request):
    """Get all activities"""
    try:
        activities = Activity.objects.select_related('id__id_location').prefetch_related('id__picture_set').all()
        serializer = ActivitySerializer(activities, many=True)
        return Response({
            'activities': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def activity_detail(request, activity_id):
    """Get a specific activity by ID"""
    try:
        activity = Activity.objects.select_related('id__id_location').prefetch_related('id__picture_set').get(id=activity_id)
        serializer = ActivitySerializer(activity)
        return Response({
            'activity': serializer.data
        }, status=status.HTTP_200_OK)
    except Activity.DoesNotExist:
        return Response({'error': 'Activity not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Add Landmark and Activity views
def add_landmark(request):
    """View for adding new landmarks"""
    if request.method == 'POST':
        form = CombinedLandmarkForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create Location
                    location = Location.objects.create(
                        id=uuid.uuid4(),
                        city=form.cleaned_data['city'],
                        province=form.cleaned_data['province'],
                        coordinates=form.cleaned_data['coordinates']
                    )
                    
                    # Create Marker
                    marker = Marker.objects.create(
                        id=uuid.uuid4(),
                        name=form.cleaned_data['name'],
                        description=form.cleaned_data['description'],
                        contact=form.cleaned_data['contact'],
                        url=form.cleaned_data['url'] or '',
                        min_price=form.cleaned_data['min_price'],
                        max_price=form.cleaned_data['max_price'],
                        id_location=location
                    )
                    
                    # Create Landmark
                    landmark = Landmark.objects.create(
                        id=marker,
                        story=form.cleaned_data['story']
                    )
                    
                    # Create Pictures if URLs provided
                    picture_urls = form.cleaned_data.get('picture_urls', [])
                    for url in picture_urls:
                        Picture.objects.create(
                            id=uuid.uuid4(),
                            id_marker=marker,
                            url=url
                        )
                    
                    messages.success(request, f'Landmark "{marker.name}" created successfully!')
                    return redirect('add_landmark')
                    
            except Exception as e:
                messages.error(request, f'Error creating landmark: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CombinedLandmarkForm()
    
    return render(request, 'core/add_landmark.html', {'form': form})


def add_activity(request):
    """View for adding new activities"""
    if request.method == 'POST':
        form = CombinedActivityForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Create Location
                    location = Location.objects.create(
                        id=uuid.uuid4(),
                        city=form.cleaned_data['city'],
                        province=form.cleaned_data['province'],
                        coordinates=form.cleaned_data['coordinates']
                    )
                    
                    # Create Marker
                    marker = Marker.objects.create(
                        id=uuid.uuid4(),
                        name=form.cleaned_data['name'],
                        description=form.cleaned_data['description'],
                        contact=form.cleaned_data['contact'],
                        url=form.cleaned_data['url'] or '',
                        min_price=form.cleaned_data['min_price'],
                        max_price=form.cleaned_data['max_price'],
                        id_location=location
                    )
                    
                    # Create Activity
                    activity = Activity.objects.create(
                        id=marker
                    )
                    
                    # Create Pictures if URLs provided
                    picture_urls = form.cleaned_data.get('picture_urls', [])
                    for url in picture_urls:
                        Picture.objects.create(
                            id=uuid.uuid4(),
                            id_marker=marker,
                            url=url
                        )
                    
                    messages.success(request, f'Activity "{marker.name}" created successfully!')
                    return redirect('add_activity')
                    
            except Exception as e:
                messages.error(request, f'Error creating activity: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CombinedActivityForm()
    
    return render(request, 'core/add_activity.html', {'form': form})


# Template views
def home(request):
    if request.user.is_authenticated:
        template_name = 'core/home_authenticated.html'
    else:
        template_name = 'core/home_guest.html'
    
    return render(request, template_name, {
        'user': request.user if request.user.is_authenticated else None
    })


def login_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'core/login.html')


def register_page(request):
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Basic validation
        if password != password_confirm:
            messages.error(request, "Passwords don't match.")
            return render(request, 'core/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'core/register.html')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'core/register.html')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            auth_login(request, user)
            messages.success(request, f'Welcome to Garuda, {user.username}!')
            return redirect('home')
        except Exception as e:
            messages.error(request, 'Registration failed. Please try again.')
    
    return render(request, 'core/register.html')


def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('home')
