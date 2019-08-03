from .models import (User,Spots,Images,Tags,TypesUserAction,UserActions,
	SpotTags)
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

class TagsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Tags
		fields = ('__all__')

class TypesUserActionSerializer(serializers.ModelSerializer):
	class Meta:
		model = TypesUserAction
		fields = ('__all__')

class UserActionsSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserActions
		fields = ('__all__')

class SpotTagsSerializer(serializers.ModelSerializer):
	class Meta:
		model = SpotTags
		fields = ('__all__')
