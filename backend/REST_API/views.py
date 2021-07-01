from rest_framework import viewsets, status
from rest_framework.filters import SearchFilter
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
    serializer_class = CompSerializer

    def get_queryset(self):
        queryset = CompanyInfo.objects.all()

        # 쿼리스트링 종류
        code_request = self.request.query_params.get("code", None)
        com_name = self.request.query_params.get("company", None)

        # 쿼리스트링을 사용한 경우
        if code_request is not None:  # 조건 검색 로직 필요
            queryset = CompanyInfo.objects.filter(code=code_request)
        elif com_name is not None:
            queryset = CompanyInfo.objects.filter(company=com_name)

        return queryset


class DailyPriceViewSet(viewsets.ModelViewSet):
    # GET, POST, DELETE 메서드 정의 가능. queryset, serializer_class 는 GET 메서드에 속함.
    queryset = DailyPrice.objects.all()
    serializer_class = DailyPriceSerializer

class CompanyStateViewSet(viewsets.ModelViewSet):
    queryset = CompanyState.objects.all()
    serializer_class = CompanyStateSerializer

