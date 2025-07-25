from django import forms
from orm_center.models import Landmark, Activity, Marker, Location, Picture
import uuid
import re


def convert_google_maps_to_postgis(coordinates_str):
    """
    Convert Google Maps coordinate format to PostGIS POINT format
    Input: "-6.249843959180328, 106.72179805118446" (latitude, longitude)
    Output: "POINT(106.72179805118446 -6.249843959180328)" (longitude latitude)
    """
    coordinates_str = coordinates_str.strip()
    
    # Remove any POINT wrapper if already exists
    if coordinates_str.upper().startswith('POINT'):
        return coordinates_str
    
    # Try to parse Google Maps format (latitude, longitude)
    # Pattern matches: optional whitespace, number (with optional decimal), comma, optional whitespace, number
    pattern = r'^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$'
    match = re.match(pattern, coordinates_str)
    
    if match:
        latitude = float(match.group(1))
        longitude = float(match.group(2))
        # PostGIS format is POINT(longitude latitude)
        return f"POINT({longitude} {latitude})"
    
    # If it doesn't match Google Maps format, assume it's already in correct format
    return coordinates_str


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['city', 'province', 'coordinates']
        widgets = {
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter city name'
            }),
            'province': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter province name'
            }),
            'coordinates': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter coordinates (e.g., -6.249843, 106.721798)',
                'help_text': 'Use Google Maps format: latitude, longitude'
            }),
        }

    def clean_coordinates(self):
        coordinates = self.cleaned_data.get('coordinates')
        if coordinates:
            try:
                return convert_google_maps_to_postgis(coordinates)
            except Exception as e:
                raise forms.ValidationError(f'Invalid coordinate format: {str(e)}')
        return coordinates


class MarkerForm(forms.ModelForm):
    class Meta:
        model = Marker
        fields = ['name', 'description', 'contact', 'url', 'min_price', 'max_price']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter landmark/activity name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter detailed description',
                'rows': 4
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact information'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter website URL (optional)'
            }),
            'min_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Minimum price in IDR'
            }),
            'max_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Maximum price in IDR'
            }),
        }


class LandmarkForm(forms.ModelForm):
    class Meta:
        model = Landmark
        fields = ['story']
        widgets = {
            'story': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter the historical story or legend of this landmark',
                'rows': 6
            }),
        }


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = []  # Activity model only has the id field which is a OneToOneField to Marker


class PictureForm(forms.Form):
    """
    Form for adding multiple pictures to a marker
    """
    picture_urls = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter image URLs, one per line',
            'rows': 4
        }),
        help_text='Enter one image URL per line. These will be associated with the landmark/activity.',
        required=False
    )

    def clean_picture_urls(self):
        urls = self.cleaned_data.get('picture_urls', '')
        if not urls.strip():
            return []
        
        url_list = []
        for line in urls.strip().split('\n'):
            url = line.strip()
            if url:
                # Basic URL validation
                if not (url.startswith('http://') or url.startswith('https://')):
                    raise forms.ValidationError(f'Invalid URL: {url}. URLs must start with http:// or https://')
                url_list.append(url)
        
        return url_list


class CombinedLandmarkForm(forms.Form):
    """
    Combined form for creating a landmark with location, marker, and pictures
    """
    # Location fields
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter city name'
        })
    )
    province = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter province name'
        })
    )
    coordinates = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coordinates (e.g., -6.249843, 106.721798)'
        }),
        help_text='Use Google Maps format: latitude, longitude'
    )
    
    # Marker fields
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter landmark name'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter detailed description',
            'rows': 4
        })
    )
    contact = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter contact information'
        })
    )
    url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter website URL (optional)'
        })
    )
    min_price = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum price in IDR'
        })
    )
    max_price = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maximum price in IDR'
        })
    )
    
    # Landmark specific field
    story = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the historical story or legend of this landmark',
            'rows': 6
        })
    )
    
    # Pictures
    picture_urls = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter image URLs, one per line',
            'rows': 4
        }),
        help_text='Enter one image URL per line (optional)'
    )

    def clean_coordinates(self):
        coordinates = self.cleaned_data.get('coordinates')
        if coordinates:
            try:
                return convert_google_maps_to_postgis(coordinates)
            except Exception as e:
                raise forms.ValidationError(f'Invalid coordinate format: {str(e)}')
        return coordinates

    def clean_picture_urls(self):
        urls = self.cleaned_data.get('picture_urls', '')
        if not urls.strip():
            return []
        
        url_list = []
        for line in urls.strip().split('\n'):
            url = line.strip()
            if url:
                if not (url.startswith('http://') or url.startswith('https://')):
                    raise forms.ValidationError(f'Invalid URL: {url}. URLs must start with http:// or https://')
                url_list.append(url)
        
        return url_list


class CombinedActivityForm(forms.Form):
    """
    Combined form for creating an activity with location, marker, and pictures
    """
    # Location fields
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter city name'
        })
    )
    province = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter province name'
        })
    )
    coordinates = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coordinates (e.g., -6.249843, 106.721798)'
        }),
        help_text='Use Google Maps format: latitude, longitude'
    )
    
    # Marker fields
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter activity name'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter detailed description',
            'rows': 4
        })
    )
    contact = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter contact information'
        })
    )
    url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter website URL (optional)'
        })
    )
    min_price = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Minimum price in IDR'
        })
    )
    max_price = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Maximum price in IDR'
        })
    )
    
    # Pictures
    picture_urls = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Enter image URLs, one per line',
            'rows': 4
        }),
        help_text='Enter one image URL per line (optional)'
    )

    def clean_coordinates(self):
        coordinates = self.cleaned_data.get('coordinates')
        if coordinates:
            try:
                return convert_google_maps_to_postgis(coordinates)
            except Exception as e:
                raise forms.ValidationError(f'Invalid coordinate format: {str(e)}')
        return coordinates

    def clean_picture_urls(self):
        urls = self.cleaned_data.get('picture_urls', '')
        if not urls.strip():
            return []
        
        url_list = []
        for line in urls.strip().split('\n'):
            url = line.strip()
            if url:
                if not (url.startswith('http://') or url.startswith('https://')):
                    raise forms.ValidationError(f'Invalid URL: {url}. URLs must start with http:// or https://')
                url_list.append(url)
        
        return url_list