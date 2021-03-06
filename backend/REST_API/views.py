from rest_framework import viewsets
from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter
from .models import CompanyInfo, DailyPrice, CompanyState
from .serializers import *
from .filter_sets import *

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

# class CompViewSet(viewsets.ModelViewSet):
#     serializer_class = CompSerializer  # 필수 작성
#
#     def get_queryset(self, **kwargs):
#         if kwargs.get('code') is None:  # request가 없다면
#             comp_queryset = CompanyInfo.objects.all()  # 모든 정보를 불러온다.
#             comp_queryset_serializer = CompSerializer(comp_queryset, many=True).data
#             return comp_queryset_serializer
#
#         else:  # request가 있다면
#             comp_queryset = kwargs.get('code')  # 종목코드에 해당하는 정보를 불러온다.
#             comp_queryset_serializer = CompSerializer(comp_queryset).data.get(code=comp_queryset)
#             return comp_queryset_serializer

# 문제를 작게 나눠서 처리하기
class CompViewSet(viewsets.ModelViewSet):
    # 필수 구현 : 미구현시 에러
    queryset = CompanyInfo.objects.all()
    serializer_class = CompSerializer

    # 필터
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = CompFilter



class DailyPriceViewSet(viewsets.ModelViewSet):

    queryset = DailyPrice.objects.all()
    serializer_class = DailyPriceSerializer

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = DailyPriceFilter



class CompanyStateViewSet(viewsets.ModelViewSet):

    queryset = CompanyState.objects.all()
    serializer_class = CompanyStateSerializer

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = CompanyStatesFilter
    # filterset_fields = ['code', 'year', 'company_nm', 'sec']


class CalRequestViewSet(viewsets.ModelViewSet):
    queryset = CalRequest.objects.all()
    serializer_class = CalRequestSerializer

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = CalRequestFilter

class CalResponseViewSet(viewsets.ModelViewSet):
    queryset = CalResponse.objects.all()
    serializer_class = CalResponseSerializer

    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = CalResponseFilter

    # 매번 사용?
    # def get_queryset(self):
    #     queryset = CompanyState.objects.all()
    #     filter_backends = [DjangoFilterBackend]
    #     filterset_fileds  = ['code', 'year']
    #     # 종목코드를 검색했을때 빠른 속도로 검색이 되어진 반면 기업명으로 검색했을때는 브라우저가 멈춰버렸다.
    #     # 서버쪽 페이징처리와 이를 검색할수 있는 알고리즘이 필요하다.
    #     # request = self.kwargs['year']
    #     # kwargs = self.kwargs
    #
    #     code = self.request.query_params.get("code", None)
    #     year = self.request.query_params.get("year", None)
    #
    #     # & 쿼리를 할 수 있도록 코드 만들기.
    #     if self.request.query_params:
    #         queryset = CompanyState.objects.filter(code=code, year=year)
    #
    #     return queryset
