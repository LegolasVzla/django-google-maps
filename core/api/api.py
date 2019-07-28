from .models import (User,Spots,Images)
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated
from .serializers import (UserSerializer,SpotsSerializer,ImagesSerializer)
from django.contrib.auth import get_user_model

User = get_user_model()

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = UserSerializer

class SpotsViewSet(viewsets.ModelViewSet):
	queryset = Spots.objects.all().filter(is_active=True,is_deleted=False).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = SpotsSerializer

class ImagesViewSet(viewsets.ModelViewSet):
	queryset = Images.objects.all()
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = ImagesSerializer
