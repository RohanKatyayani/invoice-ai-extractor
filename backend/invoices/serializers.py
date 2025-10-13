from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    """
    Converts Invoice model instances to JSON and back.
    This serializer handles:
    - Converting database objects to API responses
    - Validating incoming API data
    - Controlling which fields are exposed via API
    """

    class Meta:
        model = Invoice
        fields = [
            'id',                 # Auto-generated ID
            'invoice_date',       # Extraction target
            'invoice_number',     # Extraction target
            'amount',             # Extraction target
            'due_date',           # Extraction target
            'original_file',      # Uploaded PDF
            'uploaded_at',        # Auto timestamp
            'extraction_method',  # LLM, regex, etc.
            'confidence_score',   # 0.0 to 1.0
        ]
        read_only_fields = [
            'id',
            'uploaded_at',
            'extraction_method',
            'confidence_score'
        ]

    def create(self, validated_data):
        """
        Custom create method to handle file uploads.
        Automatically assigns the current user.
        """
        # Get the current user from the request context
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model - handles user registration and profile.

    Used for:
    - User registration (creating new users)
    - User profile management
    - Authentication endpoints
    """

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}  # Never return password in API responses
        }

    def create(self, validated_data):
        """
        Create a new user with encrypted password.

        This overrides the default create method to ensure
        passwords are properly hashed using Django's auth system.
        """
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user