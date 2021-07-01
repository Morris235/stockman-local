from rest_framework import serializers
from .models import CompanyInfo, DailyPrice, CompanyState


# 필요한 테이블만 serializer
class CompSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CompanyInfo
        fields = ('code', 'company', 'last_update')


class DailyPriceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DailyPrice
        fields = ('code', 'date', 'open', 'high', 'low', 'close', 'diff', 'volume')


class CompanyStateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CompanyState
        fields = ('code', 'year', 'sec', 'sec_nm', 'company_nm', 'rp_type', 'mk', 'last_update',
                  'current_asset', 'gross_profit', 'net_profit', 'operating_profit', 'liabilities', 'mk_cap',
                  'number_of_stocks',
                  'current_ratio', 'debt_ratio', 'quick_ratio', 'bis',
                  'sales_growth_rate', 'asset_growth_rate', 'net_profit_growth_rate',
                  'eps', 'roa', 'gross_margin',
                  'pbr', 'per', 'roe', 'bps', 'asset_turnover')
