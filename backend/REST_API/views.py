from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response

from .models import CompanyInfo, DailyPrice, CompanyState
from .serializers import CompSerializer, DailyPriceSerializer, CompanyStateSerializer


# rest_framework에 있는 viewset에서 modelViewSet을 가져와 연동시킨다.
# seriallizer틀을 먼저 작성해야함
# serializer와 model 연동

class CompViewSet(viewsets.ModelViewSet):
    # GET, POST, DELETE 메서드 정의 가능. queryset, serializer_class 는 GET 메서드에 속함.
    queryset = CompanyInfo.objects.all()  # 예제에선 CompanyInfo.objects.all() 이였음. 다른 예제들도 참고 필요
    serializer_class = CompSerializer

class DailyPriceViewSet(viewsets.ModelViewSet):
    # GET, POST, DELETE 메서드 정의 가능. queryset, serializer_class 는 GET 메서드에 속함.
    queryset = DailyPrice.objects.all()
    serializer_class = DailyPriceSerializer

class CompanyStateViewSet(viewsets.ModelViewSet):
    queryset = CompanyState.objects.all()
    serializer_class = CompanyStateSerializer

