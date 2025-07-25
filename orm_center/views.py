from django.shortcuts import render
from rest_framework.response import Response
from .models import Marker
from django.contrib import messages
from rest_framework import status


# Create your views here.
def get_all_markers():
  try:
    markers = Marker.objects.all()
  except:
    return Response({
                'error': 'Failed to get markers'
            }, status=status.HTTP_401_UNAUTHORIZED)
  return Response({
    'message': 'Getting markers successful',
    'markers': markers
  })
