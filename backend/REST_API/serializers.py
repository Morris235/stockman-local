from rest_framework import serializers
from .models import CompanyInfo, DailyPrice, CompState

# 필요한 테이블만 serializer
class CompSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CompanyInfo
        fields = ('code', 'company', 'last_update')

class DailyPriceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DailyPrice
        fields = ('code', 'date', 'open', 'high', 'low', 'close', 'diff', 'volume')

class CompStateSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CompState
        fields = ('code', 'date', 'account_nm', 'equity', 'last_equity', 'liabilities', 'currentLiabilities'
                  'last_liabilities', 'currentAssets', 'revenue', 'last_revenue', 'inventories',
                  'netIncome', 'last_netIncome', 'operatingExpenses', 'financialIncome', 'financeCosts', 'nonOperExpenses',
                  'corporateTax')
