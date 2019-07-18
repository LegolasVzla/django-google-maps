from django.conf.urls import include, url
from django.conf.urls.static import static
from rest_framework import routers
from .api import (UserViewSet,SpotsViewSet,ImagesViewSet)

router = routers.DefaultRouter()
router.register('api/user', UserViewSet, 'user')
router.register('api/spots', SpotsViewSet, 'spots')
router.register('api/images', ImagesViewSet, 'images')

urlpatterns = []

urlpatterns += router.urls

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)