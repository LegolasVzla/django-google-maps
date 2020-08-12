from .models import (User,Spots,Images,Tags,TypesUserAction,
	UserActions,SpotTags)
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .serializers import (UserSerializer,SpotsSerializer,ImagesSerializer,
	TagsSerializer,TypesUserActionSerializer,UserActionsSerializer,
	SpotTagsSerializer,SpotsAPISerializer,PlaceInformationAPISerializer,
	NearbyPlacesAPISerializer)
from core.settings import (max_distance)
from django.contrib.auth import get_user_model

from rest_framework.response import Response
from rest_framework import (status)
from rest_framework.decorators import action
from functools import wraps
import logging
import json

from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import Distance
from decimal import Decimal

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

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
		if self.action in ['place_information']:
			return PlaceInformationAPISerializer
		if self.action in ['nearby_places']:
			return NearbyPlacesAPISerializer			
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

	@validate_type_of_request
	@action(methods=['post'], detail=False)
	def place_information(self, request, *args, **kwargs):
		'''
		- POST method (post): get information about a place from
		latitude and longitude using geopy
		- Mandatory: latitude, longitude
		'''
		try:
			serializer = PlaceInformationAPISerializer(data=kwargs['data'])

			if serializer.is_valid():

				self.data['place_information'] = {}
				try:

					geolocator = Nominatim(user_agent="My_django_google_maps_app",timeout=3)
					location = geolocator.reverse(kwargs['data']['latitude']+", "+kwargs['data']['longitude'])

					if(location):
						try:
							self.data['place_information']['country_name']=location.raw['address']['country']
							self.data['place_information']['country_code']=location.raw['address']['country_code'].upper()
						except Exception as e:
							self.data['place_information']["country_name"]="undefined"
							self.data['place_information']["country_code"]="undefined"
						try:
							self.data['place_information']['state_name']=location.raw['address']['state']
						except Exception as e:
							self.data['place_information']["state_name"]="undefined"
						try:
							self.data['place_information']['city_name']=location.raw['address']['city']
						except Exception as e:
							self.data['place_information']["city_name"]="undefined"
						try:
							self.data['place_information']['postal_code']=location.raw['address']['postcode']
						except Exception as e:
							self.data['place_information']["postal_code"]="undefined"
						try:
							self.data['place_information']['full_address']=location.raw['display_name']
						except Exception as e:
							self.data['full_address']="undefined"
						self.code = status.HTTP_200_OK

				except (GeocoderTimedOut) as e:
					for i,j in data.items():
						self.data['place_information'][i] = "undefined. Not found information"
					# This also could be 204 to display some different
					# message in front end layer
					self.code = status.HTTP_200_OK
					#self.code = status.HTTP_204_NO_CONTENT

				self.response_data['data'].append(self.data)

			else:
				return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			logging.getLogger('error_logger').exception("[API - SpotsViewSet] - Error: " + str(e))
			self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
			self.response_data['error'].append("[API - SpotsViewSet] - Error: " + str(e))
		return Response(self.response_data,status=self.code)

	@validate_type_of_request
	@action(methods=['post'], detail=False)
	def nearby_places(self, request, *args, **kwargs):
		'''
		- POST method (post): get the nearby places of
		the requested user
		- Mandatory: latitude, longitude, max distance, user_id
		'''
		try:
			serializer = NearbyPlacesAPISerializer(data=kwargs['data'])

			if serializer.is_valid():

				self.data['nearby'] = []

                # Transform current latitude and longitude of the user, in a geometry point
				point_of_user = GEOSGeometry("POINT({} {})".format(kwargs['data']['longitude'],kwargs['data']['latitude']))
                
				if(Spots.objects.filter(
					position__distance_lte=(point_of_user,Distance(km=max_distance)),
					is_active=True,
					is_deleted=False,
					user=kwargs['data']['user']
				).exists()):

					# Get all the nearby places within a 5 km that match wit Spots of the current user
					queryset = Spots.objects.filter(
						position__distance_lte=(point_of_user,Distance(km=max_distance)),
						is_active=True,
						is_deleted=False
					).values('lat','lng').order_by('id')

					for i in queryset:
						self.data['nearby'].append(i)

				else:
					self.code = status.HTTP_204_NO_CONTENT

				self.response_data['data'].append(self.data)

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

