from .models import (User,Spots)
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .serializers import (UserSerializer,SpotsSerializer)
from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = UserSerializer

class SpotsViewSet(viewsets.ModelViewSet):
	queryset = Spots.objects.all()
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = SpotsSerializer
