from django.db import models


# Create your models here.
# 地区和片区表
class RegionDistrict(models.Model):
    id = models.IntegerField(primary_key=True)
    region = models.CharField(max_length=255, blank=True, null=True, db_comment='地区')
    district = models.CharField(max_length=255, blank=True, null=True, db_comment='片区')
    area_down = models.CharField(max_length=255, blank=True, null=True, db_comment='片区下对应')

    class Meta:
        managed = False
        db_table = 'region_district'
        db_table_comment = '地区-片区对应表'


# 片区原始数据总表
class ElectricSatrtSumData(models.Model):
    district = models.CharField(max_length=255, db_comment='片区')
    generation_summation = models.FloatField(blank=True, null=True, db_comment='发电总和')
    file_generation = models.FloatField(blank=True, null=True, db_comment='火电发电')
    water_generation = models.FloatField(blank=True, null=True, db_comment='水电发电')
    take_generation = models.FloatField(blank=True, null=True, db_comment='抽蓄发电')
    wind_generation = models.FloatField(blank=True, null=True, db_comment='风电发电')
    light_generation = models.FloatField(blank=True, null=True, db_comment='光伏发电')
    little_file_generation = models.FloatField(blank=True, null=True, db_comment='小火电发电')
    little_water_generation = models.FloatField(blank=True, null=True, db_comment='小水电发电')
    receive_generation = models.FloatField(blank=True, null=True, db_comment='受电')
    real_time_generation = models.FloatField(blank=True, null=True, db_comment='实时用电')
    backup_generation_sum = models.FloatField(blank=True, null=True, db_comment='正备用总和')
    file_generation_backup = models.FloatField(blank=True, null=True, db_comment='火电正备用')
    water_generation_backup = models.FloatField(blank=True, null=True, db_comment='水电正备用')
    take_generation_backup = models.FloatField(blank=True, null=True, db_comment='抽蓄正备用')
    lose_backup_generation_sum = models.FloatField(blank=True, null=True, db_comment='负备用总和')
    file_generation_backup_lose = models.FloatField(blank=True, null=True, db_comment='火电负备用')
    water_generation_backup_lose = models.FloatField(blank=True, null=True, db_comment='水电负备用')
    take_generation_backup_lose = models.FloatField(blank=True, null=True, db_comment='抽蓄负备用')
    datatimes = models.CharField(max_length=255, db_comment='日期')
    timing = models.CharField(max_length=255, db_comment='时间')

    class Meta:
        managed = False
        db_table = 'electric_satrt_sum_data'
        unique_together = (('id', 'district', 'datatimes'),)
        db_table_comment = '片区开始数据总表'


# 火电发电功率
class FlreQuantity(models.Model):
    district = models.CharField(max_length=255, db_comment='片区')
    electric_quantity = models.FloatField(blank=True, null=True, db_comment='电量')
    flag = models.IntegerField(blank=True, null=True, db_comment='1 新能源消纳场景， 2 供电最大场景')
    datatimes = models.CharField(max_length=255, blank=True, null=True, db_comment='日期')
    timing = models.CharField(max_length=255, blank=True, null=True, db_comment='时间')

    class Meta:
        managed = False
        db_table = 'flre_quantity'
        unique_together = (('id', 'district'),)
        db_table_comment = '新能源消纳场景/供电最大场景   火电发电功率'



class WaterQuantity(models.Model):
    district = models.CharField(max_length=255, db_comment='片区')
    electric_quantity = models.FloatField(blank=True, null=True, db_comment='电量')
    flag = models.IntegerField(blank=True, null=True, db_comment='1 新能源消纳场景， 2 供电最大场景')
    datatimes = models.CharField(max_length=255, blank=True, null=True, db_comment='日期')
    timing = models.CharField(max_length=255, blank=True, null=True, db_comment='时间')

    class Meta:
        managed = False
        db_table = 'water_quantity'
        unique_together = (('id', 'district'),)
        db_table_comment = '新能源消纳场景/供电最大场景   水电发电功率'
