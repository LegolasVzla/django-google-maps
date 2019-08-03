from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
from django.http import (HttpResponse, HttpResponseForbidden, 
	HttpResponseRedirect)
#from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
#from rest_framework.permissions import IsAuthenticated
from core.settings import (API_KEY,FONT_AWESOME_KEY,defaultLat,defaultLng,
    max_distance)
from rest_framework import status
from api.models import (User,Spots,Images,Tags,TypesUserAction,
    UserActions,SpotTags)
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import Distance
from decimal import Decimal

import json
import requests

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
        #print(content)
        return render(request, 'index.html',content)
'''
class DemoView(APIView):

def get(self, request, *args, **kwargs):
content = {}
content["message"] = 'Hello World'
return render(request, 'demo.html',content)
'''
class SpotView(APIView):

    def get(self, request, *args, **kwargs):
        data = {}

        if request.method == 'GET':

            # Request to get information about the place clicked
            if request.GET['action']=="get_spot_modal":
                data['code'] = status.HTTP_200_OK
                data['lat'] = request.GET['lat']
                data['lng'] = request.GET['lng']

            # Request to display nearby places
            elif request.GET['action']== "get_nearby_places":
                current_latitude = Decimal(request.GET['lat'])
                current_longitude = Decimal(request.GET['lng'])

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

            # Request to get information about an specific place to attempt edition
            elif request.GET['action'] == "edit_spot_modal":
                response = requests.get("http://localhost:8000/api/spots/"+str(request.GET['spot_id']))
                response = response.content.decode('utf-8')
                json_response = json.loads(response)
                data['id'] = json_response['id']
                data['spotName'] = json_response['name']
                data['country'] = json_response['country']
                data['country_code'] = json_response['country_code']
                data['city'] = json_response['city']
                data['postal_code'] = json_response['postal_code']
                data['lat'] = json_response['lat']
                data['lng'] = json_response['lng']
                data['code'] = status.HTTP_200_OK

        else:
            data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

    def post(self, request, *args, **kwargs):
        data = {}
        
        # Request to create a new place
        if request.method == 'POST':

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
                    type_user_action_id=int(1),
                    spot_id=spot_id
                )
                user_action.save()
                user_action_id = UserActions.objects.latest('id').id

                # Iterate over the tag list
                for current_tag_name in request.POST.get('tagList').split(','):

                    # Check if the current tag already exist
                    if(Tags.objects.filter(name=current_tag_name,is_active=True,is_deleted=False).exists()):
                        
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

                    # Type User Action case: Spot Tag
                    type_user_action = TypesUserAction.objects.get(id=int(1))

                    # Generate a new spot tag
                    spot_tag = SpotTags(
                        user_action_id=user_action_id,
                        tag_id=current_tag_id
                    )
                    spot_tag.save()

        else:
            data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

    def put(self, request, *args, **kwargs):
        data = {}

        # User is sending spot data to update
        if request.method == 'PUT':

            spot = Spots.objects.get(id=request.POST['spotId'])
            spot.name = request.POST['name']
            spot.save()
            data['code'] = status.HTTP_200_OK

        else:
            data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')


    def delete(self, request, *args, **kwargs):
        data = {}

        # A spot is requested by the user to remove it 
        if request.method == 'DELETE':
            spot = Spots.objects.get(id=request.POST.get('spot_id'))
            spot.is_active = False
            spot.is_deleted = True
            spot.save()
            data['placeName'] = spot.name
            data['code'] = status.HTTP_200_OK

        else:
            data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')