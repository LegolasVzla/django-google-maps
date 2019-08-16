from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
from django.http import (HttpResponse, HttpResponseForbidden, 
	HttpResponseRedirect)
#from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
from core.settings import (API_KEY,FONT_AWESOME_KEY,defaultLat,defaultLng,
    max_distance)
from rest_framework import status
from api.models import (User,Spots,Images,Tags,TypesUserAction,
    UserActions,SpotTags)
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import Distance
from decimal import Decimal

from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

import json
import requests
import logging

# Create your views here.
class IndexView(APIView):

    def get(self, request, *args, **kwargs):
        content = {}
        response = requests.get("http://localhost:8000/api/spots/")
        response = response.content.decode('utf-8')
        json_response = json.loads(response)
        content['api_key'] = API_KEY
        if FONT_AWESOME_KEY:
            content['fontawesome_key'] = FONT_AWESOME_KEY
        else:
            content['fontawesome_key'] = ''
        content['defaultLat'] = defaultLat 
        content['defaultLng'] = defaultLng

        try:
            content['data'] = json_response
        except Exception as e:
            content['data'] = {'name':'Not found information'}
        return render(request, 'index.html',content)

class SpotView(APIView):

    def get(self, request, *args, **kwargs):
        data = {}

        if request.method == 'GET':

            # Request to get information about the place clicked
            if request.GET['action']=="get_spot_modal":
                data['code'] = status.HTTP_200_OK
                data['lat'] = request.GET['lat']
                data['lng'] = request.GET['lng']
                try:
                    geolocator = Nominatim(user_agent="My_django_google_maps_app",timeout=3)
                    location = geolocator.reverse(request.GET['lat']+", "+request.GET['lng'])
                    if(location):
                        try:
                            data['country_name']=location.raw['address']['country']
                            data['country_code']=location.raw['address']['country_code'].upper()
                        except Exception as e:
                            data["country_name"]="undefined"
                            data["country_code"]="undefined"
                        try:
                            data['state_name']=location.raw['address']['state']
                        except Exception as e:
                            data["state_name"]="undefined"
                        try:
                            data['city_name']=location.raw['address']['city']
                        except Exception as e:
                            data["city_name"]="undefined"
                        try:
                            data['postal_code']=location.raw['address']['postcode']
                        except Exception as e:
                            data["postal_code"]="undefined"
                        try:
                            data['full_address']=location.raw['display_name']
                        except Exception as e:
                            data['full_address']="undefined"
                except (GeocoderTimedOut) as e:
                    for i,j in data.items():
                        data[i] = "undefined"

            # Request to display nearby places
            elif request.GET['action']== "get_nearby_places":
                current_latitude = Decimal(request.GET['lat'])
                current_longitude = Decimal(request.GET['lng'])

                try:
                    # Transform current latitude and longitude of the user, in a geometry point
                    point_of_user = GEOSGeometry("POINT({} {})".format(current_longitude, current_latitude))
                    
                    if(Spots.objects.filter(position__distance_lte=(point_of_user,Distance(km=max_distance)),is_active=True,is_deleted=False).exists()):

                        # Get all the nearby places within a 5 km that match wit Spots of the current user
                        spots_in_range = Spots.objects.filter(position__distance_lte=(point_of_user,Distance(km=max_distance)),is_active=True,is_deleted=False).values('lat','lng').order_by('id')

                        data['code'] = status.HTTP_200_OK

                        nearby_list = []
                        for i in spots_in_range:
                            nearby_list.append(i)
                        data['nearby'] = nearby_list

                    else:
                        data['code'] = status.HTTP_204_NO_CONTENT

                except Exception as e:
                    logging.getLogger('error_logger').error("Error in nearby: " + str(e))

            # Request to get information about an specific place to attempt edition
            elif request.GET['action'] == "edit_spot_modal":

                try:
                    response = requests.get("http://localhost:8000/api/spots/"+str(request.GET['spot_id']))
                    response = response.content.decode('utf-8')
                    json_response = json.loads(response)
                    data['id'] = json_response['id']
                    data['spotName'] = json_response['name']
                    data['country_name'] = json_response['country']
                    data['country_code'] = json_response['country_code']
                    data['state_name'] = json_response['state']
                    data['city_name'] = json_response['city']
                    data['postal_code'] = json_response['postal_code']
                    data['full_address'] = json_response['full_address']
                    data['lat'] = json_response['lat']
                    data['lng'] = json_response['lng']

                    '''If an user action list exist for the current spot with 
                    type_user_action equal to 'Spot Tag', get it'''
                    if(UserActions.objects.filter(
                        spot_id=request.GET['spot_id'],
                        type_user_action_id=1
                    ).exists()):

                        # Get the user action id related with the spot
                        user_action_id = UserActions.objects.get(
                            spot_id=request.GET['spot_id'],
                            type_user_action_id=1,
                            is_active=True,
                            is_deleted=False)

                        # Get the tag list related with the user action
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

                    else:
                        data['tagList'] = []

                    data['code'] = status.HTTP_200_OK

                except Exception as e:
                    logging.getLogger('error_logger').error("Error in Edit Spot Modal: " + str(e))

        else:
            data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

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