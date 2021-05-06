from django.contrib import admin
from REST_API.models import CompanyInfo, DailyPrice, CompanyState
# Register your models here.
admin.site.register(CompanyInfo)
admin.site.register(CompanyState)
admin.site.register(DailyPrice)

