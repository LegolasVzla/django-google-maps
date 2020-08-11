from .models import (User,Spots,Images,Tags,TypesUserAction,
	UserActions,SpotTags)
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .serializers import (UserSerializer,SpotsSerializer,ImagesSerializer,
	TagsSerializer,TypesUserActionSerializer,UserActionsSerializer,
	SpotTagsSerializer,SpotsAPISerializer)
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework import (status)
from rest_framework.decorators import action
from functools import wraps
import logging
import json

User = get_user_model()

class StandardResultsSetPagination(PageNumberPagination):
	page_size = 10
	max_page_size = 1000

def validate_type_of_request(f):
	'''
	Allows to validate the type of request for the endpoints
	'''
	@wraps(f)
	def decorator(*args, **kwargs):
		if(len(kwargs) > 0):
			# HTML template
			kwargs['data'] = kwargs
		# DRF raw data, HTML form input
		elif len(args[1].data) > 0:
			kwargs['data'] = args[1].data
		# Postman POST request made by params
		elif len(args[1].query_params.dict()) > 0:
			kwargs['data'] = args[1].query_params.dict()
		return f(*args,**kwargs)
	return decorator

class SpotsViewSet(viewsets.ModelViewSet):
	'''
	SpotsViewSet
	'''
	queryset = Spots.objects.filter(
		is_active=True,
		is_deleted=False
	).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]	
	#serializer_class = SpotsAPISerializer
	pagination_class = StandardResultsSetPagination

	def __init__(self, *args, **kwargs):
		self.response_data = {'error': [], 'data': []}
		self.data = {}
		self.code = status.HTTP_200_OK

	def get_serializer_class(self):
		if self.action in ['user_places']:
			return SpotsAPISerializer
		return SpotsSerializer

	@validate_type_of_request
	@action(methods=['post'], detail=False)
	def user_places(self, request, *args, **kwargs):
		'''
		- POST method (post): get the user places list of
		the requested user
		- Mandatory: user_id
		'''
		try:
			serializer = SpotsSerializer(
				data=kwargs['data'],
				fields=kwargs['data']['user']
			)

			if serializer.is_valid():

				queryset = Spots.objects.filter(
					is_active=True,
					is_deleted=False,
					user=kwargs['data']['user']
				).order_by('-id')

				serializer = SpotsSerializer(queryset,many=True,required_fields=['user'])
				self.data['spots']=json.loads(json.dumps(serializer.data))
				self.response_data['data'].append(self.data)
				self.code = status.HTTP_200_OK

			else:
				return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			logging.getLogger('error_logger').exception("[API - SpotsViewSet] - Error: " + str(e))
			self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
			self.response_data['error'].append("[API - SpotsViewSet] - Error: " + str(e))
		return Response(self.response_data,status=self.code)

class UserViewSet(viewsets.ModelViewSet):
	queryset = User.objects.all()
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = UserSerializer

class ImagesViewSet(viewsets.ModelViewSet):
	queryset = Images.objects.filter(is_active=True,is_deleted=False).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = ImagesSerializer

class TagsViewSet(viewsets.ModelViewSet):
	queryset = Tags.objects.filter(is_active=True,is_deleted=False).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = TagsSerializer
	pagination_class = StandardResultsSetPagination

class TypesUserActionViewSet(viewsets.ModelViewSet):
	queryset = TypesUserAction.objects.filter(is_active=True,is_deleted=False).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = TypesUserActionSerializer

class UserActionsViewSet(viewsets.ModelViewSet):
	queryset = UserActions.objects.filter(is_active=True,is_deleted=False).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = UserActionsSerializer

class SpotTagsViewSet(viewsets.ModelViewSet):
	queryset = SpotTags.objects.filter(is_active=True,is_deleted=False).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = SpotTagsSerializer

