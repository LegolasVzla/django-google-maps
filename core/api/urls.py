from django.conf.urls import include, url
from django.conf.urls.static import static
from rest_framework import routers
from .api import (UserViewSet)

router = routers.DefaultRouter()
router.register('api/user', UserViewSet, 'user')

urlpatterns = []

urlpatterns += router.urls

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)