from django.conf.urls import include, url
from django.conf.urls.static import static
from rest_framework import routers
from django.urls import path
from frontend import views

router = routers.DefaultRouter()

urlpatterns = []

urlpatterns += router.urls

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
