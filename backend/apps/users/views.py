"""Views for users."""

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserRegistrationSerializer


class UserRegistrationView(generics.CreateAPIView):
    """Open registration endpoint."""

    permission_classes = []
    serializer_class = UserRegistrationSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get/update current user profile."""

    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class UserDeleteAccountView(generics.DestroyAPIView):
    """Delete current user account (anonymize PD)."""

    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        user = request.user
        # Anonymize personal data
        user.email = f"deleted_{user.id}@deleted.local"
        user.first_name = ""
        user.last_name = ""
        user.set_unusable_password()
        user.agreed_to_pd = False
        user.is_active = False
        user.save()
        return Response(
            {"detail": "Аккаунт деактивирован, персональные данные анонимизированы."},
            status=status.HTTP_200_OK,
        )
