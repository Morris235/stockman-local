from django.contrib import admin
from django.urls import path, re_path
from . import views
from REST_API import views
from django.conf.urls import include
from rest_framework import routers

from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()
router.register(r'company', views.CompViewSet, basename='comp')
router.register(r'daily_price', views.DailyPriceViewSet, basename='daily')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include((router.urls, 'rest_framework.urls'), namespace='api')),
    re_path(r'^', include(router.urls)),
    # path('', views.ReactAppView.as_view()),
]

# urlpatterns += router.urls
