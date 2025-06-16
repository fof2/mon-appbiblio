from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from appbiblio import views 
from django.shortcuts import redirect




urlpatterns = [  
    path('admin/', admin.site.urls),
    path('', include('appbiblio.urls')),
    path('', views.home, name='home'),
    path('gestion/', lambda request: redirect('home')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)