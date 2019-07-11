from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import View, TemplateView
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.response import Response
#from rest_framework.permissions import IsAuthenticated
#from api.user.serializers import UserModelSerializer
from core.settings import API_KEY

# Create your views here.
class IndexView(APIView):
    def get(self, request):
        content = {'message': 'Welcome!'}
        return Response(content)

class MapView(APIView):
    def get(self, request, *args, **kwargs):
    	#content = {'key': API_KEY }
        return render(request, 'index.html',{'api_key':API_KEY})