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
        fields = ('code', 'company_nm', 'set_base_date', 'update', 'sec', 'sec_nm', 'mk'
                  'rp_type', 'current_ratio', 'debt_ratio', 'quick_ratio', 'bis',
                  'fin_badness', 'sales_growth_rate', 'asset_growth_rate',
                  'net_profit_growth_rate', 'eps', 'roa',
                  'gross_margin', 'pbr', 'per', 'roe', 'asset_turnover')
