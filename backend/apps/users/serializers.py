"""Serializers for users."""

from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "role", "agreed_to_pd", "created_at")
        read_only_fields = ("id", "created_at", "role")


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    agreed_to_pd = serializers.BooleanField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ("email", "password", "agreed_to_pd")

    def validate_agreed_to_pd(self, value):
        if not value:
            raise serializers.ValidationError(
                "Необходимо дать согласие на обработку персональных данных."
            )
        return value

    def create(self, validated_data):
        validated_data.pop("agreed_to_pd", None)
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
