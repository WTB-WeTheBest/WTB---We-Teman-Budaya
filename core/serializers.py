from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .validators import validate_email_format, validate_username_format, validate_secure_password
from orm_center.models import Landmark, Marker, Location, Picture, Activity


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_secure_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm')
        extra_kwargs = {
            'email': {'required': True, 'validators': [validate_email_format]},
            'username': {'validators': [validate_username_format]},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def validate_email(self, value):
        # Custom format validation is handled by the validator in Meta
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
    def validate_username(self, value):
        # Custom format validation is handled by the validator in Meta
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        return value
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'date_joined')
        read_only_fields = ('id', 'username', 'date_joined')


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ('id', 'coordinates', 'city', 'province')


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Picture
        fields = ('id', 'url')


class MarkerSerializer(serializers.ModelSerializer):
    location = LocationSerializer(source='id_location', read_only=True)
    pictures = PictureSerializer(source='picture_set', many=True, read_only=True)
    
    class Meta:
        model = Marker
        fields = ('id', 'name', 'description', 'contact', 'url', 'min_price', 'max_price', 'location', 'pictures')


class LandmarkSerializer(serializers.ModelSerializer):
    marker = MarkerSerializer(source='id', read_only=True)
    
    class Meta:
        model = Landmark
        fields = ('story', 'marker')


class ActivitySerializer(serializers.ModelSerializer):
    marker = MarkerSerializer(source='id', read_only=True)
    
    class Meta:
        model = Activity
        fields = ('marker',)