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

    def post(self, request, *args, **kwargs):
        print (request.POST)
        #import pdb;pdb.set_trace() 
        data = {}
    
        # User already clicked a point 
        if 'lat' and 'lng' in request.POST:
            data['code'] = status.HTTP_200_OK
            data['lat'] = request.POST['lat']
            data['lng'] = request.POST['lng']

        # User is sending spot data to save
        elif 'latitude' and 'length' in request.POST:
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

        else:
            data['code'] = status.HTTP_400_BAD_REQUEST

        return HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')        
        #return HttpResponse(request, 'index.html',data)
