from django.shortcuts import render
from django.http import (HttpResponse, HttpResponseForbidden, 
	HttpResponseRedirect)
#from django.core.exceptions import ObjectDoesNotExist
from rest_framework.views import APIView
#from rest_framework.permissions import IsAuthenticated
from core.settings import API_KEY
from rest_framework import status
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
        try:
            content['data'] = json_response
        except Exception as e:
            content['data'] = {'name':'Not found information'}
        #print(content)
        return render(request, 'index.html',content)