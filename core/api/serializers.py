from .models import (User,Spots,Images)
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('__all__')

class SpotsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Spots
		fields = ('__all__')

class ImagesSerializer(serializers.ModelSerializer):
	class Meta:
		model = Images
		fields = ('__all__')
