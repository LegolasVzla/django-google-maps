from django.conf.urls import include, url
from django.conf.urls.static import static
from django.urls import path
from frontend import views
#from .views import (IndexView)

urlpatterns = [
    url(r'^index/', views.IndexView.as_view(), name='index'),
    url(r'^spot/', views.SpotView.as_view(), name='spot'),
    url(r'^spot/nearby/', views.SpotView.as_view(), name='spotNearby'),
    url(r'^spot/create/', views.SpotView.as_view(), name='spotCreate'),
    url(r'^spot/editSpotModal/', views.SpotView.as_view(), name='editSpotModal'),
    url(r'^spot/update/', views.SpotView.as_view(), name='spotUpdate'),
    url(r'^spot/delete/', views.SpotView.as_view(), name='spotDelete')    
#    url(r'^map/', views.MapView.as_view(), name='map')
]

#urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
