from django.shortcuts import render
from django.core.serializers.json import DjangoJSONEncoder
from django.http import (HttpResponse, HttpResponseForbidden, 
	HttpResponseRedirect)
#from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
#from rest_framework.permissions import IsAuthenticated
from core.settings import API_KEY,FONT_AWESOME_KEY,defaultLat,defaultLng
from rest_framework import status
from api.models import (Spots)

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
        content['fontawesome_key'] = FONT_AWESOME_KEY
        content['defaultLat'] = defaultLat 
        content['defaultLng'] = defaultLng         

        try:
            content['data'] = json_response
        except Exception as e:
            content['data'] = {'name':'Not found information'}
        #print(content)
        return render(request, 'index.html',content)

class SpotView(APIView):

    def post(self, request, *args, **kwargs):
        print ("POST",request.POST)
        data = {}
    
        # User already clicked a point 
        if request.POST['method'] == "get":
            data['code'] = status.HTTP_200_OK
            data['lat'] = request.POST['lat']
            data['lng'] = request.POST['lng']

        # User is sending spot data to create
        elif request.POST['method'] == "create":
            data['code'] = status.HTTP_200_OK
            spotData = Spots(
                user_id=1,
                name=request.POST.get('placeName'),
                city=request.POST['city'],
                geom = GEOSGeometry("POINT({} {})".format(request.POST.get('length'), request.POST.get('latitude'))),
                position = GEOSGeometry("POINT({} {})".format(request.POST.get('length'), request.POST.get('latitude'))),
                country=request.POST['country'],
                country_code=request.POST['countryCode'],
                lat=request.POST['latitude'],
                lng=request.POST['length']
                )
            spotData.save()

        # A spot is requested by the user to attempt edition
        elif request.POST['method'] == "editSpotModal":
            response = requests.get("http://localhost:8000/api/spots/"+str(request.POST['spot_id']))
            response = response.content.decode('utf-8')
            json_response = json.loads(response)
            data['id'] = json_response['id']
            data['spotName'] = json_response['name']
            data['country'] = json_response['country']
            data['country_code'] = json_response['country_code']
            data['city'] = json_response['city']
            data['lat'] = json_response['lat']
            data['lng'] = json_response['lng']
            data['code'] = status.HTTP_200_OK

        # User is sending spot data to update
        elif request.POST['method'] == "update":
            spot = Spots.objects.get(id=request.POST['spotId'])
            spot.name = request.POST['name']
            spot.save()
            data['code'] = status.HTTP_200_OK

        # User is request nearby places
        elif request.POST['method'] == "get_nearby":
            max_distance=5  # 5 km by default, this could be customizable
            current_latitude = Decimal(request.POST['lat'])
            current_longitude = Decimal(request.POST['lng'])

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

        else:            
            data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')

    def put(self, request, *args, **kwargs):
        data = {}

        # An spot is requested by the user to remove it 
        if request.POST['method'] == "delete":
            spot = Spots.objects.get(id=request.POST.get('spot_id'))
            spot.is_active = False
            spot.is_deleted = True
            spot.save()
            data['placeName'] = spot.name
            data['code'] = status.HTTP_200_OK

        else:
            data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')