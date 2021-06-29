from rest_framework import viewsets, status
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import HttpResponse
from rest_framework.response import Response
from .models import CompanyInfo, DailyPrice, CompanyState
from .serializers import CompSerializer, DailyPriceSerializer, CompanyStateSerializer


# rest_framework에 있는 viewset에서 modelViewSet을 가져와 연동시킨다.
# seriallizer틀을 먼저 작성해야함
# serializer와 model 연동

# class CompViewSet(viewsets.ModelViewSet):
#     # GET, POST, DELETE 메서드 정의 가능. queryset, serializer_class 는 GET 메서드에 속함.
#     queryset = CompanyInfo.objects.all()  # 예제에선 CompanyInfo.objects.all() 이였음. 다른 예제들도 참고 필요
#     serializer_class = CompSerializer

# class CompViewSet(viewsets.ModelViewSet):
#     def get_queryset(self, **kwargs):
#         if kwargs.get('code') is None:
#             comp_queryset = CompanyInfo.objects.all()  # 모든 정보를 불러온다.
#             comp_queryset_serializer = CompSerializer(comp_queryset, many=True)
#             return Response(comp_queryset_serializer.data, status=status.HTTP_200_OK)
#         else:
#             code = kwargs.get('code')  # 종목코드에 해당하는 정보를 불러온다.
#             comp_serializer = CompSerializer(CompanyInfo.objects.get(code=code))
#             return Response(comp_serializer.data, status=status.HTTP_200_OK)

class CompViewSet(viewsets.ModelViewSet):
    def get(self, request):
        code = self.request.query_params.get('code', None)

        queryset = CompanyInfo.objects.all()
        serializer_class = CompSerializer(queryset, many=True)
        if code:
            queryset = queryset.filter(code=code)
            serializer_class = CompSerializer(queryset, many=True)
        return serializer_class


class DailyPriceViewSet(viewsets.ModelViewSet):
    # GET, POST, DELETE 메서드 정의 가능. queryset, serializer_class 는 GET 메서드에 속함.
    queryset = DailyPrice.objects.all()
    serializer_class = DailyPriceSerializer

class CompanyStateViewSet(viewsets.ModelViewSet):
    queryset = CompanyState.objects.all()
    serializer_class = CompanyStateSerializer

