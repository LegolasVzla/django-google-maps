from .models import (User,Spots,Images,Tags,TypesUserAction,UserActions,
	SpotTags)
from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A Serializer that takes an additional `fields` argument that
    controls which fields should be used.
    """
    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop("fields", None)
        excluded_fields = kwargs.pop("excluded_fields", None)
        required_fields = kwargs.pop("required_fields", None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

            if isinstance(fields, dict):
                for field, config in fields.items():
                    set_attrs(self.fields[field], config)

        if excluded_fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            for field_name in excluded_fields:
                self.fields.pop(field_name)

        if required_fields is not None:
            for field_name in required_fields:
                self.fields[field_name].required = True

class UserSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ('__all__')

class SpotsSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
	class Meta:
		model = Spots
		fields = ('__all__')

class SpotsAPISerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='id',required=True)
    class Meta:
        model = Spots
        fields = ('user',)

class ImagesSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
	class Meta:
		model = Images
		fields = ('__all__')

class TagsSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
	class Meta:
		model = Tags
		fields = ('__all__')

class TypesUserActionSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
	class Meta:
		model = TypesUserAction
		fields = ('__all__')

class UserActionsSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
	class Meta:
		model = UserActions
		fields = ('__all__')

class SpotTagsSerializer(DynamicFieldsModelSerializer,serializers.ModelSerializer):
	class Meta:
		model = SpotTags
		fields = ('__all__')
