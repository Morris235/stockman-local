"""
파라미터명과 필터 조건키가 다른 경우 필터셋 클래스를 만들어서 사용
"""

from django_filters import rest_framework as filters
from .models import CompanyInfo, DailyPrice, CompanyState


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

    # mk_cap
    min_mk_cap = filters.NumberFilter(field_name='mk_cap', lookup_expr='gte')
    max_mk_cap = filters.NumberFilter(field_name='mk_cap', lookup_expr='lte')

    # current_ratio
    min_current_ratio = filters.NumberFilter(field_name='current_ratio', lookup_expr='gte')
    max_current_ratio = filters.NumberFilter(field_name='current_ratio', lookup_expr='lte')

    # debt_ratio
    min_debt_ratio = filters.NumberFilter(field_name='debt_ratio', lookup_expr='gte')
    max_debt_ratio = filters.NumberFilter(field_name='debt_ratio', lookup_expr='lte')

    # quick_ratio
    min_quick_ratio = filters.NumberFilter(field_name='quick_ratio', lookup_expr='gte')
    max_quick_ratio = filters.NumberFilter(field_name='quick_ratio', lookup_expr='lte')

    # bis
    min_bis = filters.NumberFilter(field_name='bis', lookup_expr='gte')
    max_bis = filters.NumberFilter(field_name='bis', lookup_expr='lte')

    # sales_growth_rate
    min_sales_growth_rate = filters.NumberFilter(field_name='sales_growth_rate', lookup_expr='gte')
    max_sales_growth_rate = filters.NumberFilter(field_name='sales_growth_rate', lookup_expr='lte')

    # asset_growth_rate
    min_asset_growth_rate = filters.NumberFilter(field_name='asset_growth_rate', lookup_expr='gte')
    max_asset_growth_rate = filters.NumberFilter(field_name='asset_growth_rate', lookup_expr='lte')

    # net_profit_growth_rate
    min_net_profit_growth_rate = filters.NumberFilter(field_name='net_profit_growth_rate', lookup_expr='gte')
    max_net_profit_growth_rate = filters.NumberFilter(field_name='net_profit_growth_rate', lookup_expr='lte')

    # eps
    min_eps = filters.NumberFilter(field_name='eps', lookup_expr='gte')
    max_eps = filters.NumberFilter(field_name='eps', lookup_expr='lte')

    # roa
    min_roa = filters.NumberFilter(field_name='roa', lookup_expr='gte')
    max_roa = filters.NumberFilter(field_name='roa', lookup_expr='lte')

    # roe
    min_roe = filters.NumberFilter(field_name='roe', lookup_expr='gte')
    max_roe = filters.NumberFilter(field_name='roe', lookup_expr='lte')

    # gross_margin
    min_gross_margin = filters.NumberFilter(field_name='gross_margin', lookup_expr='gte')
    max_gross_margin = filters.NumberFilter(field_name='gross_margin', lookup_expr='lte')

    # pbr
    min_pbr = filters.NumberFilter(field_name='pbr', lookup_expr='gte')
    max_pbr = filters.NumberFilter(field_name='pbr', lookup_expr='lte')

    # per
    min_per = filters.NumberFilter(field_name='per', lookup_expr='gte')
    max_per = filters.NumberFilter(field_name='per', lookup_expr='lte')

    # bps
    min_bps = filters.NumberFilter(field_name='bps', lookup_expr='gte')
    max_bps = filters.NumberFilter(field_name='bps', lookup_expr='lte')

    class Meta:
        model = CompanyState
        fields = ['code', 'year', 'sec', 'sec_nm', 'company_nm', 'rp_type', 'mk', 'last_update',
                  'current_asset', 'gross_profit', 'net_profit', 'operating_profit', 'liabilities', 'mk_cap',
                  'number_of_stocks',
                  'current_ratio', 'debt_ratio', 'quick_ratio', 'bis',
                  'sales_growth_rate', 'asset_growth_rate', 'net_profit_growth_rate',
                  'eps', 'roa', 'gross_margin',
                  'pbr', 'per', 'roe', 'bps', 'asset_turnover']
