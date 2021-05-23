import datetime

from django.utils import timezone
import time

from django.db import models
# 모델의 하나의 클래스는 DB에서 하나의 테이블이다.
# 따라서 패키지 네임인 REST-API는 잘못되었음, 현재 종목이름만 가져다 쓰고 있으니 CompanyNames-REST 정도로 해야함. 그렇다는건 필요한 테이블마다 하나씩 장고 앱을 가져야 한다는 말인가?
# 모델을 다 작성하였으면 migrate 하기
# 그리고 필요없는 테이블도 분리해야함.=> 정말로 분리가 필요한가? 여기서 다 관리하고 프론트에서 필요한 데이터만 시리얼라이즈해서 내보내면 되지 않을까?

# 기업이름, 각 종목의 가격
class CompanyInfo(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    company = models.CharField(max_length=40, blank=True, null=True)
    last_update = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'company_info'


class DailyPrice(models.Model):
    code = models.CharField(primary_key=True, max_length=20)
    date = models.DateField()
    open = models.BigIntegerField(blank=True, null=True)
    high = models.BigIntegerField(blank=True, null=True)
    low = models.BigIntegerField(blank=True, null=True)
    close = models.BigIntegerField(blank=True, null=True)
    diff = models.BigIntegerField(blank=True, null=True)
    volume = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'daily_price'
        constraints = [
            models.UniqueConstraint(fields=['code', 'date'], name='company code and update')
        ]


class CompanyState(models.Model):
    # 기업코드
    code = models.CharField(primary_key=True, max_length=20, unique=True)
    # 연도
    year = models.SmallIntegerField(blank=False, null=False)
    # 업종 코드
    sec = models.CharField(max_length=10, blank=False, null=False)
    # 업종명
    sec_nm = models.CharField(max_length=50, blank=False, null=False)
    # 기업명
    company_nm = models.CharField(max_length=20, blank=False, null=False)
    # 보고서 타입
    rp_type = models.CharField(max_length=30, blank=False, null=False)
    # 시장구분
    mk = models.CharField(max_length=40, blank=False, null=False)
    # 업데이트 날짜
    last_update = models.DateTimeField()


    # <금액>
    # 유동자산
    current_asset = models.BigIntegerField(blank=True, null=True)
    # 매출총액
    total_sales = models.BigIntegerField(blank=True, null=True)
    # 당기순이익
    net_profit = models.BigIntegerField(blank=True, null=True)
    # 영업이익
    operating_profit = models.BigIntegerField(blank=True, null=True)
    # 부채총계
    # liabilities = models.BigIntegerField(blank=True, null=True)

    # <안정성 지표>
    # 유동비율
    current_ratio = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)
    # 부채비율
    debt_ratio = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)
    # 당좌비율
    quick_ratio = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)
    # 자기자본율
    bis = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)

    # <성장성 지표>
    # 매출액 증가율
    sales_growth_rate = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)
    # 총자산증가율 max_digits=7, decimal_places=3 -> 1111.234
    asset_growth_rate = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)
    # 순이익증가율
    net_profit_growth_rate = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)

    # <수익성 지표>
    # 주당순이익
    eps = models.IntegerField(blank=True, null=True)
    # 총자산이익률
    roa = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)
    # 매출액 총이익률
    gross_margin = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)

    # <기업가치 관련 지수>
    # 주가 순자산배율
    pbr = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)
    # 주당 수익비율
    per = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)
    # 자기자본이익률
    roe = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)
    # 주당순자산
    bps = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)
    # 총자산회전율
    asset_turnover = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=3)

    class Meta:
        managed = True
        db_table = 'company_state'










# Django 관련 테이블들
class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        constraints = [
            models.UniqueConstraint(fields=['group', 'permission'], name='AuthGroupPermissions')
        ]

class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        constraints = [
            models.UniqueConstraint(fields=['content_type', 'codename'], name='AuthPermission')
        ]

class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        constraints = [
            models.UniqueConstraint(fields=['user', 'group'], name='AuthUserGroups')
        ]

class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        constraints = [
            models.UniqueConstraint(fields=['user', 'permission'], name='AuthUserUserPermissions')
        ]

class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        constraints = [
            models.UniqueConstraint(fields=['app_label', 'model'], name='DjangoContentType')
        ]

class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'

