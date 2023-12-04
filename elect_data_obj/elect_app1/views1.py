# -*-coding:utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.db import connection

from elect_app1.models import RegionDistrict, ElectricSatrtSumData


# Create your views here.

# 获取地区信息
def get_region(request):
    if request.method == 'GET':
        district_data = RegionDistrict.objects.all().values('region', 'district')
        area_list = []  # 转成list后json序列化
        for a in district_data:
            area_list.append({'region': a['region'], 'district': a['district']})
        # 然后通过jsonResponse返回给请求方, 这里是list而不是dict, 所以safe需要传入False.
        result_data = {
            "message": '成功',
            "code": 200,
            'data': area_list,
        }
        return JsonResponse(result_data, json_dumps_params={'ensure_ascii': False},
                            content_type='application/json, charset=utf-8')


# 获取初始数据 左1
def get_elect_start(request):
    if request.method == 'POST':
        region = request.POST.get('region')
        region_m = RegionDistrict.objects.get(region=region)

        print(region)
        district = request.POST.get('district')

        if district:
            district_data = ElectricSatrtSumData.objects.filter(district=district, region=region).values(
                'district', 'file_generation', 'water_generation', 'take_generation', 'wind_generation',
                'light_generation', 'timing', 'receive_generation')
        else:
            pass

        result_list = []
        for a in district_data:
            result_list.append({'district': a['district'],
                                'file_generation': a['file_generation'],
                                'water_generation': a['water_generation'],
                                'take_generation': a['take_generation'],
                                'wind_generation': a['wind_generation'],
                                'light_generation': a['light_generation'],
                                'receive_generation': a['receive_generation'],
                                'timing': a['timing']})

        result_data = {
            "message": '成功',
            "code": 200,
            'data': result_list,
        }
        return JsonResponse(result_data, json_dumps_params={'ensure_ascii': False},
                            content_type='application/json, charset=utf-8')


# 获取初始数据计算之后的数据 右1
def get_elect_result(request):
    if request.method == 'POST':
        district = request.POST.get('district')
        flag = request.POST.get('flag')
