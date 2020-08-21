from django.conf.urls import include, url
from django.conf.urls.static import static
from rest_framework import routers
from .api import (UserViewSet,SpotsViewSet,ImagesViewSet,TagsViewSet,
	TypesUserActionViewSet,UserActionsViewSet,SpotTagsViewSet)

router = routers.DefaultRouter()
router.register('api/user', UserViewSet, 'user')
router.register('api/spots', SpotsViewSet, 'spots')
router.register('api/images', ImagesViewSet, 'images')
router.register('api/tags', TagsViewSet, 'tags')
router.register('api/types_user_action', TypesUserActionViewSet, 'types_user_action')
router.register('api/user_actions', UserActionsViewSet, 'user_actions')
router.register('api/spot_tags', SpotTagsViewSet, 'spot_tags')

urlpatterns = [
    url(r'^api/spots/user_places/$', SpotsViewSet.as_view({'post': 'user_places'}), name='user_places'),
    url(r'^api/spots/nearby_places/$', SpotsViewSet.as_view({'post': 'nearby_places'}), name='nearby_places'),
    url(r'^api/spots/create_spot/$', SpotsViewSet.as_view({'post': 'create_spot'}), name='create_spot'),
    url(r'^api/spots/delete_spot/$', SpotsViewSet.as_view({'post': 'destroy_spot'}), name='destroy_spot'),
    url(r'^api/spots/spot_details/$', SpotsViewSet.as_view({'post': 'spot_details'}), name='spot_details'),
    url(r'^api/spots/edit_spot/$', SpotsViewSet.as_view({'post': 'edit_spot'}), name='edit_spot'),
]

urlpatterns += router.urls

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)