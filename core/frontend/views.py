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
            spot_instance = SpotsViewSet()
            spot_instance.user_places(request,user='1')

            if spot_instance.code == 200:

                self.response_data['data']['spots'] = spot_instance.response_data['data'][0]['spots']
                self.response_data['data']['api_key'] = API_KEY

                if FONT_AWESOME_KEY:
                    self.response_data['data']['fontawesome_key'] = FONT_AWESOME_KEY
                else:
                    self.response_data['data']['fontawesome_key'] = ''

                self.response_data['data']['defaultLat'] = defaultLat 
                self.response_data['data']['defaultLng'] = defaultLng

            else:
                self.response_data = self.response_data['data']
                self.response_data['code'] = spot_instance.code

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
                    spot_instance = SpotsViewSet()
                    spot_instance.place_information(request,
                        latitude=request.POST['lat'],
                        longitude=request.POST['lng'])

                    if spot_instance.code == 200:

                        self.response_data['data']['place_information'] = spot_instance.response_data['data'][0]['place_information']

                    else:
                        self.response_data = self.response_data['data']
                        self.response_data['code'] = spot_instance.code

                except Exception as e:
                    logging.getLogger('error_logger').error("Error in get_spot_modal: " + str(e))
                    self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    self.response_data['error'].append("[SpotsView] - Error: " + str(e))

            # Request to display nearby places
            elif request.is_ajax() == True and request.POST['action'] == 'get_nearby_places':
                current_latitude = Decimal(request.POST['lat'])
                current_longitude = Decimal(request.POST['lng'])

                try:
                    spot_instance = SpotsViewSet()
                    spot_instance.nearby_places(request,
                        latitude=current_latitude,
                        longitude=current_longitude,
                        max_distance=max_distance,user='1'
                    )

                    if spot_instance.code == 200:

                        self.response_data['data']['nearby'] = spot_instance.response_data['data'][0]['nearby']

                    else:
                        self.response_data = self.response_data['data']
                        self.response_data['code'] = spot_instance.code

                except Exception as e:
                    logging.getLogger('error_logger').error("Error in get_nearby_places: " + str(e))
                    self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    self.response_data['error'].append("[SpotsView] - Error: " + str(e))

            # Request to create a new spot
            elif request.is_ajax() == True and request.POST['action'] == 'create_spot':

                try:
                    spot_instance = SpotsViewSet()
                    
                    if (request.POST['tagList'].split(',')[0]==''):
                        tagList=[]
                    else:
                        tagList=request.POST['tagList'].split(',')
                    spot_instance.create_spot(request,
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

                    if spot_instance.code == 200:
                        self.response_data['data']['spots'] = spot_instance.response_data['data'][0]
                        self.response_data['code'] = spot_instance.code

                    else:
                        self.response_data = self.response_data['data']
                        self.response_data['code'] = spot_instance.code

                except Exception as e:
                    logging.getLogger('error_logger').error("Error in create_spot: " + str(e))
                    self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    self.response_data['error'].append("[SpotsView] - Error: " + str(e))

            # Request to get information about an specific place to attempt edition
            elif request.is_ajax() == True and request.POST['action'] == "edit_spot_modal":

                try:
                    spot_instance = SpotsViewSet()
                    spot_instance.spot_details(request,spot_id=request.POST['spot_id'])

                    if spot_instance.code == 200:

                        self.response_data['data'] = spot_instance.response_data['data'][0]

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

        # User is sending spot data to update
        if request.is_ajax() == True and request.method == 'PUT':

            try:
                spot_instance = SpotsViewSet()

                if (request.POST['tags'].split(',')[0]==''):
                    tagList=[]
                else:
                    tagList=request.POST['tags'].split(',')

                spot_instance.edit_spot(request,
                    spot_id=request.POST['spotId'],
                    name=request.POST['name'],
                    tags=tagList
                )

                if spot_instance.code == 200:
                    self.response_data['data'] = spot_instance.response_data['data']

                else:
                    self.response_data = self.response_data['data']
                    self.response_data['code'] = spot_instance.code

            except Exception as e:
                logging.getLogger('error_logger').error("Error Editing a spot: " + str(e))
                self.code = status.HTTP_500_INTERNAL_SERVER_ERROR
                self.response_data['error'].append("[SpotsView] - Error: " + str(e))

        else:
            self.response_data = self.response_data['data']
            self.response_data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(self.response_data, cls=DjangoJSONEncoder), content_type='application/json')

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