from decimal import Decimal
import json
import logging

from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
from django.http import (HttpResponse)
from django.views.generic import View
from rest_framework import status
from rest_framework.views import APIView
from api.models import (User,Spots,Images,Tags,TypesUserAction,UserActions,
    SpotTags)
from api.api import (SpotsViewSet)
import boto3
from botocore.exceptions import NoCredentialsError
import requests

from core.settings import (API_KEY,FONT_AWESOME_KEY,defaultLat,defaultLng,
    max_distance)

class IndexView(View):

    def __init__(self,*args, **kwargs):
        self.response_data = {'error': [], 'data': {}, 'code': status.HTTP_200_OK}

    def get(self, request, *args, **kwargs):
        try:
            spotInstance = SpotsViewSet()
            spotInstance.user_places(request,user='1')

            if spotInstance.code == 200:

                self.response_data['data']['spots'] = spotInstance.response_data['data'][0]['spots']
                self.response_data['data']['api_key'] = API_KEY

                if FONT_AWESOME_KEY:
                    self.response_data['data']['fontawesome_key'] = FONT_AWESOME_KEY
                else:
                    self.response_data['data']['fontawesome_key'] = ''

                self.response_data['data']['defaultLat'] = defaultLat 
                self.response_data['data']['defaultLng'] = defaultLng

            else:
                self.response_data = self.response_data['data']
                self.response_data['code'] = spotInstance.code

        except Exception as e:
            self.response_data['data'] = {'name':'Not found information'}
            self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_data['error'].append("[IndexView] - Error: " + str(e))
        return render(request,template_name='frontend/index.html',context=self.response_data)

class SpotView(APIView):

    def __init__(self,*args, **kwargs):
        self.response_data = {'error': [], 'data': {}, 'code': status.HTTP_200_OK}

    def post(self, request, *args, **kwargs):
        data = {}

        # Request to create a new place
        try:
            # Request to get information about the place clicked
            if request.is_ajax() == True and request.POST['action'] == 'get_spot_modal':

                try:
                    spotInstance = SpotsViewSet()
                    spotInstance.place_information(request,
                        latitude=request.POST['lat'],
                        longitude=request.POST['lng'])

                    if spotInstance.code == 200:

                        self.response_data['data']['place_information'] = spotInstance.response_data['data'][0]['place_information']

                    else:
                        self.response_data = self.response_data['data']
                        self.response_data['code'] = spotInstance.code

                except Exception as e:
                    logging.getLogger('error_logger').error("Error in get_spot_modal: " + str(e))
                    self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    self.response_data['error'].append("[SpotsView] - Error: " + str(e))

            # Request to display nearby places
            elif request.is_ajax() == True and request.POST['action'] == 'get_nearby_places':
                current_latitude = Decimal(request.POST['lat'])
                current_longitude = Decimal(request.POST['lng'])

                try:
                    spotInstance = SpotsViewSet()
                    spotInstance.nearby_places(request,
                        latitude=current_latitude,
                        longitude=current_longitude,
                        max_distance=max_distance,user='1'
                    )

                    if spotInstance.code == 200:

                        self.response_data['data']['nearby'] = spotInstance.response_data['data'][0]['nearby']

                    else:
                        self.response_data = self.response_data['data']
                        self.response_data['code'] = spotInstance.code

                except Exception as e:
                    logging.getLogger('error_logger').error("Error in get_nearby_places: " + str(e))
                    self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    self.response_data['error'].append("[SpotsView] - Error: " + str(e))

            # Request to create a new spot
            elif request.is_ajax() == True and request.POST['action'] == 'create_spot':

                try:
                    spotInstance = SpotsViewSet()
                    
                    if (request.POST['tagList'].split(',')[0]==''):
                        tagList=[]
                    else:
                        tagList=request.POST['tagList'].split(',')
                    spotInstance.create_spot(request,
                        country=request.POST['country'],
                        country_code=request.POST['countryCode'],
                        state=request.POST['state_name'],
                        city=request.POST['city'],
                        postal_code=request.POST['postalCode'],
                        full_address=request.POST['fullAddress'],
                        lat=request.POST['latitude'],
                        lng=request.POST['length'],
                        name=request.POST['placeName'],
                        tag_list=tagList,user=1
                    )

                    if spotInstance.code == 200:
                        self.response_data['data']['spots'] = spotInstance.response_data['data'][0]
                        self.response_data['code'] = spotInstance.code

                    else:
                        self.response_data = self.response_data['data']
                        self.response_data['code'] = spotInstance.code

                except Exception as e:
                    logging.getLogger('error_logger').error("Error in create_spot: " + str(e))
                    self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    self.response_data['error'].append("[SpotsView] - Error: " + str(e))

            # Request to get information about an specific place to attempt edition
            elif request.is_ajax() == True and request.POST['action'] == "edit_spot_modal":

                try:
                    spotInstance = SpotsViewSet()
                    spotInstance.spot_details(request,spot_id=request.POST['spot_id'])

                    if spotInstance.code == 200:

                        self.response_data['data'] = spotInstance.response_data['data'][0]

                    else:
                        self.response_data = self.response_data['data']

                except Exception as e:
                    logging.getLogger('error_logger').error("Error in edit_spot_modal: " + str(e))
                    self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    self.response_data['error'].append("[SpotsView] - Error: " + str(e))

            else:
                self.response_data = self.response_data['data']
                self.response_data['code'] = status.HTTP_400_BAD_REQUEST

        except Exception as e:
            logging.getLogger('error_logger').error("Error Creating a new spot: " + str(e))
            self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_data['error'].append("[SpotsView] - Error: " + str(e))

        return HttpResponse(json.dumps(self.response_data, cls=DjangoJSONEncoder), content_type='application/json')

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
            self.response_data = self.response_data['data']
            self.response_data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

    def delete(self, request, *args, **kwargs):
        data = {}

        # A spot is requested by the user to remove it
        if request.method == 'DELETE':

            try:
                _delete_spot = SpotsViewSet()
                _delete_spot.destroy_spot(request,spot_id=request.data['spot_id'])

                if _delete_spot.code == 200:
                    self.response_data['data']['placeName'] = _delete_spot.response_data['data'][0]['placeName']

                else:
                    self.response_data['data'] = self.response_data['data']
                    self.response_data['code'] = _delete_spot.code

            except Exception as e:
                logging.getLogger('error_logger').error("Error Deleting a spot: " + str(e))

        else:
            self.response_data = self.response_data['data']
            self.response_data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(self.response_data, cls=DjangoJSONEncoder), content_type='application/json')