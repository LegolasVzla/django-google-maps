import logging
import json
from decimal import Decimal
from functools import wraps

from .models import (User,Spots,Images,Tags,TypesUserAction,
	UserActions,SpotTags)
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import Distance
from rest_framework import viewsets, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from .serializers import (UserSerializer,SpotsSerializer,ImagesSerializer,
	TagsSerializer,TypesUserActionSerializer,UserActionsSerializer,
	SpotTagsSerializer,UserPlacesAPISerializer,PlaceInformationAPISerializer,
	NearbyPlacesAPISerializer,CreateSpotAPISerializer,SpotDetailsAPISerializer,
	EditSpotAPISerializer)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

from core.settings import (max_distance,S3_ACCESS_KEY,S3_SECRET_KEY,
	s3_bucket_name,s3_env_folder_name)

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
	pagination_class = StandardResultsSetPagination

	def __init__(self, *args, **kwargs):
		self.response_data = {'error': [], 'data': []}
		self.data = {}
		self.code = status.HTTP_200_OK

	def get_serializer_class(self):
		if self.action in ['create_spot']:
			return CreateSpotAPISerializer
		if self.action in ['user_places']:
			return UserPlacesAPISerializer
		if self.action in ['place_information']:
			return PlaceInformationAPISerializer
		if self.action in ['nearby_places']:
			return NearbyPlacesAPISerializer
		if self.action in ['spot_details']:
			return SpotDetailsAPISerializer
		if self.action in ['edit_spot']:
			return EditSpotAPISerializer			
		return SpotsSerializer

	@validate_type_of_request
	@action(methods=['post'], detail=False)
	def user_places(self, request, *args, **kwargs):
		'''
		- POST method: get the user places list of
		the requested user
		- Mandatory: user_id
		'''
		try:
			serializer = UserPlacesAPISerializer(data=kwargs['data'])

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
		- POST method: get information about a place from
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
		- POST method: get the nearby places of
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

	@validate_type_of_request
	@action(methods=['post'], detail=False)
	def create_spot(self, request, *args, **kwargs):
		'''
		- POST method: create a new place
		- Mandatory: 
		- Optionals: tag list, image list
		'''
		try:
			serializer = CreateSpotAPISerializer(
				data=kwargs['data'],
				required_fields=['name','country','country_code','state','city','full_address','postal_code','lat','lng'])

			if serializer.is_valid():
				serializer = SpotsSerializer(data=kwargs['data'])

				if serializer.is_valid():
					serializer.save()

					if kwargs['data']['tag_list']:

						SpotTagsViewSet().create_spot_tags(serializer.id,kwargs['data']['tag_list'])

	                # if request.POST.get('image'):

	                #     local_file = '<path_to_the_file>'
	                #     filename = request.POST.get('placeName')
	                #     user_id = 1
	                #     key = '{}/{}/{}'.format(s3_env_folder_name,user_id,filename)

	                #     s3 = boto3.client('s3', aws_access_key_id=S3_ACCESS_KEY,aws_secret_access_key=S3_SECRET_KEY)
	                #     s3.upload_file(local_file, s3_bucket_name, key, ExtraArgs={'ACL':'public-read'})
	                #     print("Upload Successful")
	                #     bucket_location = s3.get_bucket_location(Bucket=s3_bucket_name)
	                #     #file_url = '{}/{}/{}/{}'.format(s3.meta.endpoint_url, s3_bucket_name, s3_env_folder_name, filename)
	                #     file_url = "https://s3-{0}.amazonaws.com/{1}/{2}/{3}/{4}".format(bucket_location['LocationConstraint'],s3_bucket_name,s3_env_folder_name,user_id,filename)

				else:
					return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

				self.response_data['data'].append(serializer.data)
				self.code = status.HTTP_200_OK

			else:
				return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			logging.getLogger('error_logger').exception("[API - SpotsViewSet] - Error: " + str(e))
			self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
			self.response_data['error'].append("[API - SpotsViewSet] - Error: " + str(e))
		except FileNotFoundError:
			logging.getLogger('error_logger').error("Error Saving the image, the file was not found: " + str(e))
			data['code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
		except NoCredentialsError:
			logging.getLogger('error_logger').error("Error Saving the image, AWS S3 credentials not available: " + str(e))
			data['code'] = status.HTTP_500_INTERNAL_SERVER_ERROR

		return Response(self.response_data,status=self.code)

	@validate_type_of_request
	@action(methods=['delete'], detail=False)
	def destroy_spot(self, request, *args, **kwargs):
		'''
		- DELETE method: to delete a spot with all the instances related
		- Mandatory: spot_id
		'''
		try:
			serializer = SpotsSerializer(data=kwargs['data'],fields=['id'])

			if serializer.is_valid():

				spot = Spots.objects.get(id=request.POST.get('spot_id'))
				spot.is_active = False
				spot.is_deleted = True
				spot.save()

				'''If an user action list exist for the current spot with 
				type_user_action equal to 'Spot Tag', delete it'''
				if(UserActions.objects.filter(
					spot_id=request.POST.get('spot_id'),
					is_active=True,
					is_deleted=False,
					type_user_action_id=1
				).exists()):

					user_action = UserActions.objects.get(
						spot_id=request.POST.get('spot_id'),
						type_user_action_id=1,
						is_active=True,
						is_deleted=False
					)
					user_action.is_active = False
					user_action.is_deleted = True
					user_action.save()

					# Then, delete the spot_tag list related
					spot_tag_list = SpotTags.objects.filter(
						user_action_id=user_action.id,
						is_active=True,
						is_deleted=False
					)
					spot_tag_list.update(is_active=False,is_deleted=True)

					# Finally, check if it's necessary to delete any tag
					spot_tag_list = SpotTags.objects.filter(
						user_action_id=user_action.id,
						is_active=True,
						is_deleted=False
					)

					for current_spot_tag in spot_tag_list:

						# If the current tag doesn't exists for any other spot, delete it
						if len(SpotTags.objects.filter(tag_id=current_spot_tag.tag_id,is_active=True,is_deleted=False)) == 1:

							tag = Tags.objects.get(id=current_spot_tag.tag_id)
							tag.is_active = False                    
							tag.is_deleted = True
							tag.save()

				self.data['placeName'] = spot.name

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
	def spot_details(self, request, *args, **kwargs):
		'''
		- POST method: get the spot details
		- Mandatory: spot_id
		'''
		try:
			serializer = SpotDetailsAPISerializer(data=kwargs['data'])

			if serializer.is_valid():

				try:
					queryset = get_object_or_404(Spots,
						is_active=True,
						is_deleted=False,
						id=kwargs['data']['spot_id']
					)

					serializer = SpotsSerializer(queryset,many=False,required_fields=['id'])
					self.data['spot']=json.loads(json.dumps(serializer.data))

					self.data['tagList'] = TagsViewSet().list_tags(kwargs['data']['spot_id'])

					self.response_data['data'].append(self.data)
					self.code = status.HTTP_200_OK

				except Exception as e:
					self.code = status.HTTP_404_NOT_FOUND
					self.response_data['error'].append("[API - SpotsViewSet] - Error: " + str(e))

			else:
				return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

		except Exception as e:
			logging.getLogger('error_logger').exception("[API - SpotsViewSet] - Error: " + str(e))
			self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
			self.response_data['error'].append("[API - SpotsViewSet] - Error: " + str(e))
		return Response(self.response_data,status=self.code)

	@validate_type_of_request
	@action(methods=['post'], detail=False)
	def edit_spot(self, request, *args, **kwargs):
		'''
		- POST method: edit the spot requested
		- Mandatory: spot_id
		'''
		try:
			serializer = EditSpotAPISerializer(data=kwargs['data'])

			if serializer.is_valid():

				try:

					# Validate if spot exist
					spot = get_object_or_404(Spots,
						is_active=True,
						is_deleted=False,
						id=kwargs['data']['spot_id']
					)

				except Exception as e:
					self.code = status.HTTP_404_NOT_FOUND
					raise Exception(e)

				# New spot name?
				if spot.name != kwargs['data']['name']:
					spot.name = kwargs['data']['name']
					spot.save()
				else:
					self.data['name'] = spot.name

				# Tags to delete?
				if kwargs['data']['tags_to_delete']:
					self.data['tags_deleted'] = SpotTagsViewSet().remove_spot_tags(
						kwargs['data']['spot_id'],
						kwargs['data']['tags_to_delete']
					)
				else:
					self.data['tags_deleted'] = []

				# Tags to append?
				if kwargs['data']['new_tags']:
					self.data['new_tags'] = SpotTagsViewSet().create_spot_tags(spot.id,kwargs['data']['new_tags'])
				else:
					self.data['new_tags'] = []

				self.response_data['data'].append(self.data)
				self.code = status.HTTP_200_OK

			else:
				return Response(serializer.errors,status=self.code)

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
	queryset = Images.objects.filter(
		is_active=True,
		is_deleted=False
	).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = ImagesSerializer

class TagsViewSet(viewsets.ModelViewSet):
	queryset = Tags.objects.filter(
		is_active=True,
		is_deleted=False
	).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = TagsSerializer
	pagination_class = StandardResultsSetPagination

	def list_tags(spot_id):
		'''
		Function to list all tags related with the spot requested
		'''
		tag_list = []

		# Check if the spot requested has any tag
		if(UserActions.objects.filter(
			spot_id=spot_id,
			is_active=True,
			is_deleted=False,
			type_user_action_id=1
		).exists()):

			# Get user action related with the spot 
			user_action = UserActions.objects.get(
				spot_id=spot_id,
				type_user_action_id=1,
				is_active=True,
				is_deleted=False
			)

			# Get all the spot tag list related with the user action
			spot_tag_list = SpotTags.objects.filter(
				user_action_id=user_action.id,
				is_active=True,
				is_deleted=False
			)

			# Finally, get all the tags related with the spot 
			for current_spot_tag in spot_tag_list:

				tag = Tags.objects.get(id=current_spot_tag.tag_id)
				tag_list.append(tag.name)

		return tag_list

class TypesUserActionViewSet(viewsets.ModelViewSet):
	queryset = TypesUserAction.objects.filter(
		is_active=True,
		is_deleted=False
	).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = TypesUserActionSerializer

class UserActionsViewSet(viewsets.ModelViewSet):
	queryset = UserActions.objects.filter(
		is_active=True,
		is_deleted=False
	).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = UserActionsSerializer

	def create_user_action(self,type_user_action_id,spot_id):
		try:
			user_action = None

			# Check if exists the user action for the spot_id requested
			if(UserActions.objects.filter(
				type_user_action_id=type_user_action_id,
				spot_id=spot_id,
				is_active=True,
				is_deleted=False
			).exists()):

				# Get the user action
				user_action = UserActions.objects.get(
					type_user_action_id=type_user_action_id,
					spot_id=spot_id,
					is_active=True,
					is_deleted=False
				)

			else:
				# Generate a new spot tag user action related with the spot_id
				user_action=UserActionsSerializer(data={"type_user_action":type_user_action_id,"spot":spot_id})
				if user_action.is_valid():
					user_action.save()
				else:
					raise Exception(user_action.errors)

			return user_action

		except Exception as e:
			if user_action != None:
				user_action.delete()
			raise Exception("An error happened in create_user_action: " + str(e))

class SpotTagsViewSet(viewsets.ModelViewSet):
	queryset = SpotTags.objects.filter(
		is_active=True,
		is_deleted=False
	).order_by('id')
	permission_classes = [
		permissions.AllowAny
	]
	serializer_class = SpotTagsSerializer

	def create_spot_tags(self,spot_id,tag_list):
		'''
		This function allows to create new spot tags
		for the spot_id requested
		'''
		try:
			tag_list_created = []
			user_action = None
			spot_tag = None

			# Get or create spot tag user action related with the spot
			user_action = UserActionsViewSet().create_user_action(1,spot_id)

			# Iterate over the tag list
			for current_tag_name in tag_list:
				try:

					# Check if the current tag already exist
					current_tag = get_object_or_404(Tags,name=current_tag_name,is_active=True,is_deleted=False)

				except Exception as e:

					# Generate the new tag
					current_tag = Tags(name=current_tag_name)
					current_tag.save()

				try:

					# Check if the current spot tag already exists with the spot 
					spot_tag = get_object_or_404(SpotTags,user_action=user_action.id,tag=current_tag.id,is_active=True,is_deleted=False)

				except Exception as e:

					# Generate a new spot tag
					spot_tag = SpotTags(user_action_id=user_action.id,tag_id=current_tag.id)
					spot_tag.save()

				tag_list_created.append({
					"spot_tag_id": spot_tag.id,
					"tag_id": current_tag.id,
					"name": current_tag.name
				})

		except Exception as e:
			if user_action != None:
				user_action.delete()
			if current_tag != None:
				current_tag.delete()
			raise Exception("An error happened in create_spot_tags: " + str(e))

		return tag_list_created

	def remove_spot_tags(self,spot_id,tag_list):
		'''
		This function allows to delete all the spot tag list that are
		relate with the tag_list and the spot requested.
		
		Things to consider:
		1) It does a validation if the tags inside the tag_list exists or not
		2) The user action that are relate with the spot, won't be delete
		3) The tags that exists, won't be delete, just the spot tags 
		'''
		try:
			tag_list_deleted = []

			# Get the user action related with the spot requested
			user_action = get_object_or_404(UserActions,
				spot_id=spot_id,
				type_user_action_id=1,
				is_active=True,
				is_deleted=False
			)

	        # Iterate on each tag to check if exists or not
			for current_tag in tag_list:

				try:

					# If exist the tag
					tag = get_object_or_404(Tags,
						name=current_tag,
						is_active=True,
						is_deleted=False
					)

					# Then, delete the current tag for the spot requested
					spot_tag = SpotTags.objects.get(
						user_action_id=user_action.id,
						tag_id=tag.id,
						is_active=True,
						is_deleted=False
					)

					spot_tag.is_active = False
					spot_tag.is_deleted = True
					spot_tag.save()

					tag_list_deleted.append({
						"spot_tag_id": spot_tag.id,
						"tag_id": tag.id,
						"name": tag.name
					})

				# The tag didn't exist, so continue with the next
				except Exception as e:
					continue

		# There isn't user action related with the spot requested,
		# so the tags requested are fake. Then, ignore them
		except Exception as e:
			pass

		return tag_list_deleted