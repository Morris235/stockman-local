from django.urls import path, re_path
from REST_API.views import *
from django.conf.urls import include
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'company', CompViewSet, basename='comp')
router.register(r'daily_price', DailyPriceViewSet, basename='daily')
router.register(r'company_state', CompanyStateViewSet, basename='comp_state')

urlpatterns = [
    re_path(r'^', include(router.urls)),
]
