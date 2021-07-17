from rest_framework import serializers
from .models import *


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
                  'revenue', 'current_asset', 'gross_profit', 'net_profit', 'operating_profit', 'liabilities', 'mk_cap',
                  'number_of_stocks',
                  'operating_margin', 'current_ratio', 'debt_ratio', 'quick_ratio', 'bis',
                  'sales_growth_rate', 'asset_growth_rate', 'net_profit_growth_rate',
                  'roa', 'roe', 'pbr',
                  'eps', 'per', 'bps', 'gross_margin', 'asset_turnover')


class CalRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CalRequest
        fields = ('id', 'operand_a', 'operand_b', 'operator')


class CalResponseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CalResponse
        fields = ('id', 'return_val')
