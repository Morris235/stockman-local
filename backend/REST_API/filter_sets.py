"""
파라미터명과 필터 조건키가 다른 경우 필터셋 클래스를 만들어서 사용
"""

from django_filters import rest_framework as filters
from .models import *

# 기업명 필터 클래스
class CompFilter(filters.FilterSet):
    # 검색어 자동완성 기능을 여기서 설정을 해줘야 한다.
    class Meta:
        model = CompanyInfo
        fields = '__all__'

# 주가 필터 클래스
class DailyPriceFilter(filters.FilterSet):
    # 날짜
    start_date = filters.DateFilter(field_name='date', lookup_expr=('gt'))
    end_date = filters.DateFilter(field_name='date', lookup_expr=('lt'))

    # 시가
    min_open = filters.NumberFilter(field_name='open', lookup_expr='gte')
    max_open = filters.NumberFilter(field_name='open', lookup_expr='lte')

    # 고가
    min_high = filters.NumberFilter(field_name='high', lookup_expr='gte')
    max_high = filters.NumberFilter(field_name='high', lookup_expr='lte')

    # 저가
    min_low = filters.NumberFilter(field_name='low', lookup_expr='gte')
    max_low = filters.NumberFilter(field_name='low', lookup_expr='lte')

    # 종가
    min_close = filters.NumberFilter(field_name='close', lookup_expr='gte')
    max_close = filters.NumberFilter(field_name='close', lookup_expr='lte')

    # 전일차
    min_diff = filters.NumberFilter(field_name='diff', lookup_expr='gte')
    max_diff = filters.NumberFilter(field_name='diff', lookup_expr='lte')

    # 거래량
    min_volume = filters.NumberFilter(field_name='volume', lookup_expr='gte')
    max_volume = filters.NumberFilter(field_name='volume', lookup_expr='lte')

    class Meta:
        model = DailyPrice
        fields = ['code', 'date', 'open', 'high', 'low', 'close', 'diff', 'volume']


# 재무 필터 클래스
class CompanyStatesFilter(filters.FilterSet):
    # 연도
    # start_year = filters.NumberFilter(field_name='year', lookup_expr='gte')
    # end_year = filters.NumberFilter(field_name='year', lookup_expr='lte')

    # mk_cap
    min_mk_cap = filters.NumberFilter(field_name='mk_cap', lookup_expr='gte')
    max_mk_cap = filters.NumberFilter(field_name='mk_cap', lookup_expr='lte')

    # 매출액
    min_revenue = filters.NumberFilter(field_name='revenue', lookup_expr='gte')
    max_revenue = filters.NumberFilter(field_name='revenue', lookup_expr='lte')

    # 매출총이익
    min_gross_profit = filters.NumberFilter(field_name='gross_profit', lookup_expr='gte')
    max_gross_profit = filters.NumberFilter(field_name='gross_profit', lookup_expr='lte')

    # 영업이익
    min_operating_profit = filters.NumberFilter(field_name='operating_profit', lookup_expr='gte')
    max_operating_profit = filters.NumberFilter(field_name='operating_profit', lookup_expr='lte')

    # 당기순이익
    min_net_profit = filters.NumberFilter(field_name='net_profit', lookup_expr='gte')
    max_net_profit = filters.NumberFilter(field_name='net_profit', lookup_expr='lte')

    # 영업이익률
    min_operating_margin = filters.NumberFilter(field_name='operating_margin', lookup_expr='gte')
    max_operating_margin = filters.NumberFilter(field_name='operating_margin', lookup_expr='lte')

    # 유동비율
    min_current_ratio = filters.NumberFilter(field_name='current_ratio', lookup_expr='gte')
    max_current_ratio = filters.NumberFilter(field_name='current_ratio', lookup_expr='lte')

    # 부채비율
    min_debt_ratio = filters.NumberFilter(field_name='debt_ratio', lookup_expr='gte')
    max_debt_ratio = filters.NumberFilter(field_name='debt_ratio', lookup_expr='lte')

    # 당좌비율
    min_quick_ratio = filters.NumberFilter(field_name='quick_ratio', lookup_expr='gte')
    max_quick_ratio = filters.NumberFilter(field_name='quick_ratio', lookup_expr='lte')

    # 자기자본율
    min_bis = filters.NumberFilter(field_name='bis', lookup_expr='gte')
    max_bis = filters.NumberFilter(field_name='bis', lookup_expr='lte')

    # 매출액 증가율
    min_sales_growth_rate = filters.NumberFilter(field_name='sales_growth_rate', lookup_expr='gte')
    max_sales_growth_rate = filters.NumberFilter(field_name='sales_growth_rate', lookup_expr='lte')

    # 총자산증가율
    min_asset_growth_rate = filters.NumberFilter(field_name='asset_growth_rate', lookup_expr='gte')
    max_asset_growth_rate = filters.NumberFilter(field_name='asset_growth_rate', lookup_expr='lte')

    # 순이익증가율
    min_net_profit_growth_rate = filters.NumberFilter(field_name='net_profit_growth_rate', lookup_expr='gte')
    max_net_profit_growth_rate = filters.NumberFilter(field_name='net_profit_growth_rate', lookup_expr='lte')

    # 주당순이익
    min_eps = filters.NumberFilter(field_name='eps', lookup_expr='gte')
    max_eps = filters.NumberFilter(field_name='eps', lookup_expr='lte')

    # 총자산이익률
    min_roa = filters.NumberFilter(field_name='roa', lookup_expr='gte')
    max_roa = filters.NumberFilter(field_name='roa', lookup_expr='lte')

    # 자기자본이익률
    min_roe = filters.NumberFilter(field_name='roe', lookup_expr='gte')
    max_roe = filters.NumberFilter(field_name='roe', lookup_expr='lte')

    # 매출액 총이익률
    min_gross_margin = filters.NumberFilter(field_name='gross_margin', lookup_expr='gte')
    max_gross_margin = filters.NumberFilter(field_name='gross_margin', lookup_expr='lte')

    # 주가 순자산배율
    min_pbr = filters.NumberFilter(field_name='pbr', lookup_expr='gte')
    max_pbr = filters.NumberFilter(field_name='pbr', lookup_expr='lte')

    # 주당 수익비율
    min_per = filters.NumberFilter(field_name='per', lookup_expr='gte')
    max_per = filters.NumberFilter(field_name='per', lookup_expr='lte')

    # 주당순자산비율
    min_bps = filters.NumberFilter(field_name='bps', lookup_expr='gte')
    max_bps = filters.NumberFilter(field_name='bps', lookup_expr='lte')

    # 자본회전률
    min_asset_turnover = filters.NumberFilter(field_name='asset_turnover', lookup_expr='gte')
    max_asset_turnover = filters.NumberFilter(field_name='asset_turnover', lookup_expr='lte')

    class Meta:
        model = CompanyState
        fields = ['code', 'year', 'sec', 'sec_nm', 'company_nm', 'rp_type', 'mk', 'last_update',
                  'revenue', 'current_asset', 'gross_profit', 'net_profit', 'operating_profit', 'liabilities', 'mk_cap',
                  'number_of_stocks',
                  'operating_margin', 'current_ratio', 'debt_ratio', 'quick_ratio', 'bis',
                  'sales_growth_rate', 'asset_growth_rate', 'net_profit_growth_rate',
                  'roa', 'roe', 'pbr',
                  'eps', 'per', 'bps', 'gross_margin', 'asset_turnover']


class CalRequestFilter(filters.FilterSet):
    class Meta:
        model = CalRequest
        fields = ['id', 'operand_a', 'operand_b', 'operator']


class CalResponseFilter(filters.FilterSet):
    class Meta:
        model = CalResponse
        fields = ['id', 'return_val']
