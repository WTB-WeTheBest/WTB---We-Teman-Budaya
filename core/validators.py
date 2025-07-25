import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


def validate_email_format(value):
    """
    Validate email format using a comprehensive regex pattern.
    """
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, value):
        raise ValidationError(
            _('Enter a valid email address.'),
            code='invalid_email'
        )


def validate_username_format(value):
    """
    Validate username format:
    - 3-20 characters
    - Only letters, numbers, and underscores
    - Cannot start or end with underscore
    """
    if len(value) < 3 or len(value) > 20:
        raise ValidationError(
            _('Username must be between 3 and 20 characters long.'),
            code='invalid_length'
        )
    
    if not re.match(r'^[a-zA-Z0-9_]+$', value):
        raise ValidationError(
            _('Username can only contain letters, numbers, and underscores.'),
            code='invalid_characters'
        )
    
    if value.startswith('_') or value.endswith('_'):
        raise ValidationError(
            _('Username cannot start or end with an underscore.'),
            code='invalid_format'
        )


def validate_secure_password(value):
    """
    Validate password security requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    - At least one special character
    """
    if len(value) < 8:
        raise ValidationError(
            _('Password must be at least 8 characters long.'),
            code='password_too_short'
        )
    
    if not re.search(r'[A-Z]', value):
        raise ValidationError(
            _('Password must contain at least one uppercase letter.'),
            code='password_no_upper'
        )
    
    if not re.search(r'[a-z]', value):
        raise ValidationError(
            _('Password must contain at least one lowercase letter.'),
            code='password_no_lower'
        )
    
    if not re.search(r'\d', value):
        raise ValidationError(
            _('Password must contain at least one number.'),
            code='password_no_number'
        )
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=[\]\\\/~`]', value):
        raise ValidationError(
            _('Password must contain at least one special character (!@#$%^&*(),.?":{}|<>_-+=[]\\\/~`).'),
            code='password_no_special'
        )