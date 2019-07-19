from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
#from datetime import datetime
User = get_user_model()

# Create your models here.
class Spots(models.Model):
	name = models.CharField( max_length = 100)
	country = models.CharField( max_length = 100)
	country_code = models.CharField( max_length = 5)
	city = models.CharField( max_length = 100)	
	lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
	lng = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
	user = models.ForeignKey(User,related_name='spots_user_id',on_delete=models.CASCADE)
	is_active = models.BooleanField(default=True)
	is_deleted = models.BooleanField(default=False)
	updated_date=models.DateTimeField(auto_now=True)
	created_date = models.DateTimeField(auto_now_add=True)

class Images(models.Model):
	url = models.URLField()
	spot = models.ForeignKey(Spots,related_name='images_spot_id',on_delete=models.CASCADE)
	#extension = models.CharField( max_length = 100)
	principalimage = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	is_deleted = models.BooleanField(default=False)
	updated_date=models.DateTimeField(auto_now=True)
	created_date = models.DateTimeField(auto_now_add=True)
