from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.views.generic import View, TemplateView
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.response import Response
#from rest_framework.permissions import IsAuthenticated
#from api.user.serializers import UserModelSerializer

# Create your views here.
class IndexView(APIView):

    def get(self, request):
        content = {'message': 'Welcome!'}
        return Response(content)