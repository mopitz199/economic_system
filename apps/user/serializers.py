from django.contrib.auth.models import User

from rest_framework import serializers


class CreateUserRequest(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField(min_length=6)
    repeated_password = serializers.CharField(min_length=6)

    def validate(self, data):
        password = data.get('password')
        repeated_password = data.get('repeated_password')
        if password == repeated_password:
            return data
        else:
            raise serializers.ValidationError("Passwords are not equal")

    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            return email
        else:
            raise serializers.ValidationError("Email already exists")


class LoginSerializer(serializers.Serializer):

    username = serializers.CharField()
    password = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
        )
