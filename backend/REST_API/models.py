from django.db import models
# 모델의 하나의 클래스는 DB에서 하나의 테이블이다.
# 따라서 패키지 네임인 REST-API는 잘못되었음, 현재 종목이름만 가져다 쓰고 있으니 CompanyNames-REST 정도로 해야함. 그렇다는건 필요한 테이블마다 하나씩 장고 앱을 가져야 한다는 말인가?
# 모델을 다 작성하였으면 migrate 하기
# 그리고 필요없는 테이블도 분리해야함.=> 정말로 분리가 필요한가? 여기서 다 관리하고 프론트에서 필요한 데이터만 시리얼라이즈해서 내보내면 되지 않을까?

# class Stocks(models.Model):
#     code = models.CharField(db_column='CODE', primary_key=True)
#     date = models.DateField(db_column='DATE', primary_key=True)
#     open = models.BigIntegerField(db_column='OPEN', null=True)
#     high = models.BigIntegerField(db_column='HIGH', null=True)
#     low = models.BigIntegerField(db_column='LOW', null=True)
#     diff = models.BigIntegerField(db_column='DIFF', null=True)
#     volume = models.BigIntegerField(db_column='VOL', null=True)

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
        unique_together = (('code', 'date'),)


# class CompStateAnalysis(models.Model):
#     # 기업코드
#     code = models.CharField(primary_key=True, max_length=20)
#     # 업데이트 일자
#     date = models.DateField()
#     # 유동부채
#     currentRatio = models.FloatField(blank=True, null=True)
#     # 부채비율
#     debtRatio = models.FloatField(blank=True, null=True)
#     # 당좌비율
#     quickRatio = models.FloatField(blank=True, null=True)
#     # 자기자본율
#     BIS = models.FloatField(blank=True, null=True)
#     # 주당순자산가치
#     BPS = models.FloatField(blank=True, null=True)
#     # 매출액증가율
#     salesGrowthRate = models.FloatField(blank=True, null=True)
#     # 총자산증가율
#     totalAssetGrowthRate = models.FloatField(blank=True, null=True)
#     # 순이익증가율
#     netProfitGrowthRate = models.FloatField(blank=True, null=True)
#     # 총자산이익률
#     ROA = models.FloatField(blank=True, null=True)
#     # 매출액총이익률
#     grossMargin = models.FloatField(blank=True, null=True)
#     # 총자산회전율
#     totalAssetTurnover = models.FloatField(blank=True, null=True)
#     # 자기자본이익률
#     ROE = models.FloatField(blank=True, null=True)
#     # 재무불량도
#     financialBadness = models.FloatField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'yearly_comp_state_analysis'
#         unique_together = (('code', 'date'),)

# class CompState(models.Model):
#     # 업데이트 날짜
#     date = models.DateField()
#     # 보고서 업데이트 날짜
#     set_base_date = models.CharField(primary_key=True, max_length=20)
#     # 기업코드
#     code = models.CharField(primary_key=True, max_length=20)
#     # 기업명
#     company_name = models.CharField(max_length=40)
#     # 자본총계
#     equity = models.BigIntegerField(blank=True, null=True)
#     # 전년도 자본총계
#     last_equity = models.BigIntegerField(blank=True, null=True)
#     # 부채총계
#     liabilities = models.BigIntegerField(blank=True, null=True)
#     # 유동 부채
#     currentLiabilities = models.BigIntegerField(blank=True, null=True)
#     # 전년도 부채총계
#     last_liabilities = models.BigIntegerField(blank=True, null=True)
#     # 유동자산
#     currentAssets = models.BigIntegerField(blank=True, null=True)
#     # 매출액, 영업수익
#     revenue = models.BigIntegerField(blank=True, null=True)
#     # 전년도 매출액
#     last_revenue = models.BigIntegerField(blank=True, null=True)
#     # 재고자산
#     inventories = models.BigIntegerField(blank=True, null=True)
#     # 당기순이익
#     netIncome = models.BigIntegerField(blank=True, null=True)
#     # 전년도 당기순이익
#     last_netIncome = models.BigIntegerField(blank=True, null=True)
#     # 영업비용
#     operatingExpenses = models.BigIntegerField(blank=True, null=True)
#     # 금융수익
#     financialIncome = models.BigIntegerField(blank=True, null=True)
#     # 금융비용
#     financeCosts = models.BigIntegerField(blank=True, null=True)
#     # 영업외비용
#     nonOperExpenses = models.BigIntegerField(blank=True, null=True)
#     # 법인세
#     corporateTax = models.BigIntegerField(blank=True, null=True)
#
#     class Meta:
#         managed = True
#         db_table = 'yearly_comp_state'
#         unique_together = (('code', 'date', 'set_base_date'),)

class CompanyState(models.Model):
    # 기업코드
    code = models.CharField(primary_key=True, max_length=20)
    # 업데이트 날짜
    date = models.DateField()
    # 보고서 업데이트 날짜
    set_base_date = models.CharField(primary_key=True, max_length=20)
    # 기업명
    company_name = models.CharField(max_length=40)
    # 업종 코드
    sec = models.IntegerField()
    # 업종명
    sec_nm = models.CharField(max_length=40)
    # 시장구분
    mk = models.CharField(max_length=20)
    # 보고서 타입
    rp_type = models.CharField(max_length=40)









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
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


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
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


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
        unique_together = (('app_label', 'model'),)


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

