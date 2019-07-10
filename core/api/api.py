from .models import (User)
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .serializers import (UserSerializer)
from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	permission_classes = (IsAuthenticated,)
	serializer_class = UserSerializer
