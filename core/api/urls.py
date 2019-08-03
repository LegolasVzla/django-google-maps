from django.conf.urls import include, url
from django.conf.urls.static import static
from rest_framework import routers
from .api import (UserViewSet,SpotsViewSet,ImagesViewSet,TagsViewSet,
	TypeUserActionsViewSet,UserActionsViewSet,SpotTagsViewSet)

router = routers.DefaultRouter()
router.register('api/user', UserViewSet, 'user')
router.register('api/spots', SpotsViewSet, 'spots')
router.register('api/images', ImagesViewSet, 'images')
router.register('api/tags', TagsViewSet, 'tags')
router.register('api/types_user_action', TypeUserActionsViewSet, 'types_user_action')
router.register('api/user_actions', UserActionsViewSet, 'user_actions')
router.register('api/spot_tags', SpotTagsViewSet, 'spot_tags')

urlpatterns = []

urlpatterns += router.urls

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)