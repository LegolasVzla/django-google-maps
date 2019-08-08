from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

from django.contrib.gis.db import models
from django.contrib.postgres.operations import CreateExtension
from django.db import migrations

#from datetime import datetime
User = get_user_model()


class Migration(migrations.Migration):

    operations = [
        CreateExtension('postgis'),
    ]

# Create your models here.
class Spots(models.Model):
	name = models.CharField( max_length = 100)
	country = models.CharField( max_length = 100)
	country_code = models.CharField( max_length = 5)
	state = models.CharField( max_length = 100)
	city = models.CharField( max_length = 100)
	full_address = models.CharField( max_length = 250)
	postal_code = models.CharField( max_length = 20)
	lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
	lng = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True)
	geom = models.GeometryField(srid=4326,blank=True,null=True)
	position = models.PointField(null=True, blank=True)	
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

class Tags(models.Model):
	name = models.CharField( max_length = 100)
	is_active = models.BooleanField(default=True)
	is_deleted = models.BooleanField(default=False)
	updated_date=models.DateTimeField(auto_now=True)
	created_date = models.DateTimeField(auto_now_add=True)

class TypesUserAction(models.Model):
	name = models.CharField( max_length = 100)
	is_active = models.BooleanField(default=True)
	is_deleted = models.BooleanField(default=False)
	updated_date=models.DateTimeField(auto_now=True)
	created_date = models.DateTimeField(auto_now_add=True)

class UserActions(models.Model):
	type_user_action = models.ForeignKey(TypesUserAction,related_name='useractions_type_user_action_id',on_delete=models.CASCADE)
	spot = models.ForeignKey(Spots,related_name='useractions_spot_id',on_delete=models.CASCADE)
	is_active = models.BooleanField(default=True)
	is_deleted = models.BooleanField(default=False)
	updated_date=models.DateTimeField(auto_now=True)
	created_date = models.DateTimeField(auto_now_add=True)

class SpotTags(models.Model):
	user_action = models.ForeignKey(UserActions,related_name='spottags_user_action_id',on_delete=models.CASCADE)
	tag = models.ForeignKey(Tags,related_name='spottags_user_action_id',on_delete=models.CASCADE)
	is_active = models.BooleanField(default=True)
	is_deleted = models.BooleanField(default=False)
	updated_date=models.DateTimeField(auto_now=True)
	created_date = models.DateTimeField(auto_now_add=True)
