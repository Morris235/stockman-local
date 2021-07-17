from django.urls import path, re_path
from REST_API.views import *
from django.conf.urls import include
from rest_framework import routers

# 라우터에서(라우터란?) 디테일 리퀘스트를 어떻게 설정해서 뷰와 연결해야하나? 정규식을 사용하는건 맞는거 같은데 말이야
router = routers.DefaultRouter()
router.register(r'company', CompViewSet, basename='company-info')
router.register(r'daily-price', DailyPriceViewSet, basename='daily')
router.register(r'company-state', CompanyStateViewSet, basename='comp-state')
router.register(r'cal-request', CalRequestViewSet, basename='cal-request')
router.register(r'cal-response', CalResponseViewSet, basename='cal-response')

urlpatterns = [
    re_path(r'^', include(router.urls)),  # 정규표현식을 사용, 모든 라우터 url 표현
]
