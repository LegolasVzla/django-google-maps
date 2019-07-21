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
                country=request.POST['country'],
                country_code=request.POST['countryCode'],
                lat=request.POST['length'],
                lng=request.POST['latitude']
                )
            spotData.save()

        # An spot is requested by the user 
        elif request.POST['method'] == "update":
            response = requests.get("http://localhost:8000/api/spots/"+str(request.POST['spot_id']))
            response = response.content.decode('utf-8')
            json_response = json.loads(response)
            data['spotName'] = json_response['name']
            data['code'] = status.HTTP_200_OK

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