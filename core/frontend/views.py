from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
from django.http import (HttpResponse, HttpResponseForbidden, 
	HttpResponseRedirect)
#from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from core.settings import (API_KEY,FONT_AWESOME_KEY,defaultLat,defaultLng,
    max_distance,S3_ACCESS_KEY,S3_SECRET_KEY,s3_bucket_name)
from rest_framework import status
from api.models import (User,Spots,Images,Tags,TypesUserAction,
    UserActions,SpotTags)

from decimal import Decimal
import boto3
from botocore.exceptions import NoCredentialsError

import json
import requests
import logging

from django.views.generic import View
from api.api import (SpotsViewSet)

class IndexView(View):

    def __init__(self,*args, **kwargs):
        self.response_data = {'error': [], 'data': {}, 'code': status.HTTP_200_OK}

    def get(self, request, *args, **kwargs):
        try:
            _spots = SpotsViewSet()
            _spots.user_places(request,user='1')

            if _spots.code == 200:

                self.response_data['data']['spots'] = _spots.response_data['data'][0]['spots']
                self.response_data['data']['api_key'] = API_KEY

                if FONT_AWESOME_KEY:
                    self.response_data['data']['fontawesome_key'] = FONT_AWESOME_KEY
                else:
                    self.response_data['data']['fontawesome_key'] = ''

                self.response_data['data']['defaultLat'] = defaultLat 
                self.response_data['data']['defaultLng'] = defaultLng

            else:
                self.response_data = self.response_data['data']
                self.response_data['code'] = _spots.code

        except Exception as e:
            content['data'] = {'name':'Not found information'}
        return render(request,template_name='frontend/index.html',context=self.response_data)

class SpotView(View):

    def __init__(self,*args, **kwargs):
        self.response_data = {'error': [], 'data': {}, 'code': status.HTTP_200_OK}

    def get(self, request, *args, **kwargs):
        data = {}

        if request.method == 'GET':

            # Request to get information about the place clicked
            if request.GET['action'] == "get_spot_modal":

                try:
                    _place_information = SpotsViewSet()
                    _place_information.place_information(request,
                        latitude=request.GET['lat'],
                        longitude=request.GET['lng'])

                    if _place_information.code == 200:

                        self.response_data['data']['place_information'] = _place_information.response_data['data'][0]['place_information']

                    else:
                        self.response_data = self.response_data['data']
                        self.response_data['code'] = _place_information.code

                except Exception as e:
                    logging.getLogger('error_logger').error("Error in get_spot_moda: " + str(e))

            # Request to display nearby places
            elif request.GET['action']== "get_nearby_places":
                current_latitude = Decimal(request.GET['lat'])
                current_longitude = Decimal(request.GET['lng'])

                try:
                    _nearby_places = SpotsViewSet()
                    _nearby_places.nearby_places(request,latitude=current_latitude,longitude=current_longitude,max_distance=max_distance,user='1')

                    if _nearby_places.code == 200:

                        self.response_data['data']['nearby'] = _nearby_places.response_data['data'][0]['nearby']

                    else:
                        self.response_data = self.response_data['data']
                        self.response_data['code'] = _nearby_places.code

                except Exception as e:
                    logging.getLogger('error_logger').error("Error in get_nearby_places: " + str(e))

            # # Request to get information about an specific place to attempt edition
            # elif request.GET['action'] == "edit_spot_modal":

            #     try:
            #         response = requests.get("http://localhost:8000/api/spots/"+str(request.GET['spot_id']))
            #         response = response.content.decode('utf-8')
            #         json_response = json.loads(response)
            #         data['id'] = json_response['id']
            #         data['spotName'] = json_response['name']
            #         data['country_name'] = json_response['country']
            #         data['country_code'] = json_response['country_code']
            #         data['state_name'] = json_response['state']
            #         data['city_name'] = json_response['city']
            #         data['postal_code'] = json_response['postal_code']
            #         data['full_address'] = json_response['full_address']
            #         data['lat'] = json_response['lat']
            #         data['lng'] = json_response['lng']

            #         '''If an user action list exist for the current spot with 
            #         type_user_action equal to 'Spot Tag', get it'''
            #         if(UserActions.objects.filter(
            #             spot_id=request.GET['spot_id'],
            #             type_user_action_id=1
            #         ).exists()):

            #             # Get the user action id related with the spot
            #             user_action_id = UserActions.objects.get(
            #                 spot_id=request.GET['spot_id'],
            #                 type_user_action_id=1,
            #                 is_active=True,
            #                 is_deleted=False)

            #             # Get the tag list related with the user action
            #             spot_tag_list = SpotTags.objects.filter(
            #                 user_action_id=user_action_id.id,
            #                 is_active=True,
            #                 is_deleted=False)

            #             # Get all the tag names related with the tag list
            #             tagList = []
            #             for current_tag in spot_tag_list:
            #                 tag = Tags.objects.get(id=current_tag.tag_id)
            #                 tagList.append(tag.name)
            #             data['tagList'] = tagList

            #         else:
            #             data['tagList'] = []

            #         data['code'] = status.HTTP_200_OK

            #     except Exception as e:
            #         logging.getLogger('error_logger').error("Error in Edit Spot Modal: " + str(e))

        else:
            self.response_data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(self.response_data, cls=DjangoJSONEncoder), content_type='application/json')

    def post(self, request, *args, **kwargs):
        data = {}
        
        # Request to create a new place
        if request.method == 'POST':

            try:
                data['code'] = status.HTTP_200_OK
                spotData = Spots(
                    user_id=1,
                    name=request.POST.get('placeName'),
                    city=request.POST['city'],
                    geom = GEOSGeometry("POINT({} {})".format(request.POST.get('length'), request.POST.get('latitude'))),
                    position = GEOSGeometry("POINT({} {})".format(request.POST.get('length'), request.POST.get('latitude'))),
                    country=request.POST['country'],
                    country_code=request.POST['countryCode'],
                    postal_code=request.POST['postalCode'],                
                    lat=request.POST['latitude'],
                    lng=request.POST['length']
                )
                spotData.save()
                spot_id = Spots.objects.latest('id').id

                if request.POST.get('image'):

                    local_file = '<path_to_the_file>'
                    filename = request.POST.get('placeName')
                    user_id = 1
                    s3_env_folder_name = 'dev/spots'
                    key = '{}/{}/{}'.format(s3_env_folder_name,user_id,filename)

                    s3 = boto3.client('s3', aws_access_key_id=S3_ACCESS_KEY,aws_secret_access_key=S3_SECRET_KEY)
                    s3.upload_file(local_file, s3_bucket_name, key, ExtraArgs={'ACL':'public-read'})
                    print("Upload Successful")
                    bucket_location = s3.get_bucket_location(Bucket=s3_bucket_name)
                    #file_url = '{}/{}/{}/{}'.format(s3.meta.endpoint_url, s3_bucket_name, s3_env_folder_name, filename)
                    file_url = "https://s3-{0}.amazonaws.com/{1}/{2}/{3}/{4}".format(bucket_location['LocationConstraint'],s3_bucket_name,s3_env_folder_name,user_id,filename)

                if request.POST.get('tagList'):

                    # Generate a new user action with Type USer Action case: Spot Tag
                    user_action = UserActions(
                        type_user_action_id=1,
                        spot_id=spot_id
                    )
                    user_action.save()
                    user_action_id = UserActions.objects.latest('id').id

                    # Iterate over the tag list
                    for current_tag_name in request.POST.get('tagList').split(','):

                        # Check if the current tag already exist
                        if(Tags.objects.filter(
                            name=current_tag_name,
                            is_active=True,
                            is_deleted=False).exists()):
                            
                            # Get the tag_id
                            current_tag = Tags.objects.get(
                                name=current_tag_name,
                                is_active=True,
                                is_deleted=False
                            )
                        else:
                            
                            # Generate the new tag
                            current_tag = Tags(name=current_tag_name)
                            current_tag.save()

                        current_tag_id = Tags.objects.latest('id').id

                        # Generate a new spot tag
                        spot_tag = SpotTags(
                            user_action_id=user_action_id,
                            tag_id=current_tag_id
                        )
                        spot_tag.save()

            except Exception as e:
                logging.getLogger('error_logger').error("Error Creating a new spot: " + str(e))
                data['code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            except FileNotFoundError:
                logging.getLogger('error_logger').error("Error Saving the image, the file was not found: " + str(e))
                data['code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            except NoCredentialsError:
                logging.getLogger('error_logger').error("Error Saving the image, AWS S3 credentials not available: " + str(e))
                data['code'] = status.HTTP_500_INTERNAL_SERVER_ERROR

        else:
            data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

    def put(self, request, *args, **kwargs):
        data = {}
        temporalTagList = ['funny','amazing']

        # User is sending spot data to update
        if request.method == 'PUT':

            try:
                spot = Spots.objects.get(id=request.POST['spotId'])
                spot.name = request.POST['name']
                spot.save()

                #if request.POST.get('tagList'):
                if temporalTagList:

                    '''If an user action list exist for the current spot with
                    type_user_action equal to 'Spot Tag', get it'''
                    if(UserActions.objects.filter(
                        spot_id=request.POST.get('spot_id'),
                        type_user_action_id=1
                    )):

                        user_action_id = UserActions.objects.get(
                            spot_id=request.POST.get('spot_id'),
                            type_user_action_id=1,
                            is_active=True,
                            is_deleted=False)

                        # Get the spot tag list related
                        spot_tag_list = SpotTags.objects.filter(
                            user_action_id=user_action_id.id,
                            is_active=True,
                            is_deleted=False)                    

                        # Get all the tag names related with the tag list
                        tagList = []
                        for current_tag in spot_tag_list:
                            tag = Tags.objects.get(id=current_tag.tag_id)
                            tagList.append(tag.name)
                        data['tagList'] = tagList

                        '''Case 1: The incoming tag list is the same that
                        the stored current tag list'''
                        if(data['tagList'] == temporalTagList):
                            # Don't do anything
                            print("It's the same tag list")
                        # Case 2: The incoming tag list is different that
                        # the stored current tag list
                        else:
                            new_tag_list = []
                            for current_tag_stored in data['tagList']:
                                
                                '''if the current tag stored is not in the
                                incoming tag list, delete it'''
                                if not(current_tag_stored in temporalTagList):

                                    # Get the tag_id
                                    tag = Tags.objects.get(name=current_tag_stored)

                                    # Delete it in the spot tag
                                    spot_tag = SpotTags.objects.get(
                                        user_action_id=user_action_id.id,
                                        tag_id=tag.id,
                                        is_active=True,
                                        is_deleted=False)
                                    spot_tag.is_active = False
                                    spot_tag.is_deleted = True
                                    spot_tag.save()

                                    '''If the current tag doesn't exists for any other
                                    spot, delete it''' 
                                    if not(SpotTags.objects.filter(
                                        tag_id=tag.id,
                                        is_active=True,
                                        is_deleted=False
                                    )):

                                        tag.is_active = False
                                        tag.is_deleted = True
                                        tag.save()

                                #The current tag stored is in the incoming tag
                                # list, so keep it
                                else:
                                    temporalTagList.remove(current_tag_stored)

                            # Finally, create the new tag list
                            for new_possible_tag in temporalTagList:
                                
                                # Check if the current tag already exist
                                if(Tags.objects.get(
                                    name=new_possible_tag,
                                    is_active=True,
                                    is_deleted=False).exists()):
                                    
                                    # Get the tag_id
                                    current_tag = Tags.objects.get(
                                        name=new_possible_tag,
                                        is_active=True,
                                        is_deleted=False
                                    )

                                else:
                                    # Generate the new tag
                                    current_tag = Tags(name=new_possible_tag)
                                    current_tag.save()

                                current_tag_id = Tags.objects.latest('id').id

                                # Generate a new spot tag
                                spot_tag = SpotTags(
                                    user_action_id=user_action_id.id,
                                    tag_id=current_tag_id
                                )
                                spot_tag.save()                            

                # Case 3: The tag list is comming wihout any tag
                else:

                    '''If an user action list exist for the current spot with
                    type_user_action equal to 'Spot Tag', delete it'''
                    if(UserActions.objects.filter(
                        spot_id=request.POST.get('spot_id'),
                        type_user_action_id=1
                    )):

                        user_action_id = UserActions.objects.get(
                            spot_id=request.POST.get('spot_id'),
                            type_user_action_id=1,
                            is_active=True,
                            is_deleted=False)
                        user_action_id.is_active = False
                        user_action_id.is_deleted = True
                        user_action_id.save()

                        # Then, delete the spot_tag list related
                        user_action_id = UserActions.objects.get(
                            spot_id=request.POST.get('spot_id'),
                            type_user_action_id=1,
                            is_active=False,
                            is_deleted=True)

                        spot_tag_list = SpotTags.objects.filter(
                            user_action_id=user_action_id.id,
                            is_active=True,
                            is_deleted=False)
                        spot_tag_list.update(is_active=False,is_deleted=True)

                        # Finally, check if it's necessary to delete any tag
                        spot_tag_list = SpotTags.objects.filter(
                            user_action_id=user_action_id.id,
                            is_active=False,
                            is_deleted=True)

                        for current_spot_tag in spot_tag_list:
                            '''If the current tag doesn't exists for any other spot, 
                            delete it''' 
                            if not(SpotTags.objects.filter(
                                tag_id=current_spot_tag.tag_id,
                                is_active=True,
                                is_deleted=False
                            )):

                                tag = Tags.objects.get(id=current_spot_tag.tag_id)
                                tag.is_active = False                    
                                tag.is_deleted = True
                                tag.save()

                data['code'] = status.HTTP_200_OK

            except Exception as e:
                logging.getLogger('error_logger').error("Error Editing a spot: " + str(e))

        else:
            data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

    def delete(self, request, *args, **kwargs):
        data = {}

        # A spot is requested by the user to remove it 
        if request.method == 'DELETE':

            try:

                spot = Spots.objects.get(id=request.POST.get('spot_id'))
                spot.is_active = False
                spot.is_deleted = True
                spot.save()

                '''If an user action list exist for the current spot with 
                type_user_action equal to 'Spot Tag', delete it'''
                if(UserActions.objects.filter(
                    spot_id=request.POST.get('spot_id'),
                    type_user_action_id=1
                )):

                    user_action_id = UserActions.objects.get(
                        spot_id=request.POST.get('spot_id'),
                        type_user_action_id=1,
                        is_active=True,
                        is_deleted=False)
                    user_action_id.is_active = False
                    user_action_id.is_deleted = True
                    user_action_id.save()

                    # Then, delete the spot_tag list related
                    user_action_id = UserActions.objects.get(
                        spot_id=request.POST.get('spot_id'),
                        type_user_action_id=1,
                        is_active=False,
                        is_deleted=True)

                    spot_tag_list = SpotTags.objects.filter(
                        user_action_id=user_action_id.id,
                        is_active=True,
                        is_deleted=False)
                    spot_tag_list.update(is_active=False,is_deleted=True)

                    # Finally, check if it's necessary to delete any tag
                    spot_tag_list = SpotTags.objects.filter(
                        user_action_id=user_action_id.id,
                        is_active=False,
                        is_deleted=True)

                    for current_spot_tag in spot_tag_list:
                        '''If the current tag doesn't exists for any other spot, 
                        delete it''' 
                        if not(SpotTags.objects.filter(
                            tag_id=current_spot_tag.tag_id,
                            is_active=True,
                            is_deleted=False
                        )):

                            tag = Tags.objects.get(id=current_spot_tag.tag_id)
                            tag.is_active = False                    
                            tag.is_deleted = True
                            tag.save()

                data['placeName'] = spot.name
                data['code'] = status.HTTP_200_OK

            except Exception as e:
                logging.getLogger('error_logger').error("Error Deleting a spot: " + str(e))

        else:
            data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')