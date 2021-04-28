from django.contrib import admin
from REST_API.models import CompanyInfo, CompState, DailyPrice
# Register your models here.
admin.site.register(CompanyInfo)
admin.site.register(CompState)
admin.site.register(DailyPrice)

