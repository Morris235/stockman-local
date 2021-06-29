from django.contrib import admin
from django.urls import path
from django.conf.urls import include


urlpatterns = [
    path('api/', include('REST_API.urls')),  # '' 요청은 REST_API/urls.py에서 처리하도록 매핑
    path('admin/', admin.site.urls),
]

# urlpatterns += router.urls
