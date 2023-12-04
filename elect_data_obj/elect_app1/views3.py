# -*-coding:utf-8 -*-
import os

import pandas as pd
from django.http import HttpResponse, JsonResponse, FileResponse
from django.db import connection

send_timing = ['06:30:00', '11:30:00', '12:00:00', '18:00:00', '21:30:00']


def get_data_timing(request):
    if request.method == 'GET':
        sql = """
        SELECT distinct SUBSTR(datatimes,12) from  power_supply_clean_data
        """
        with connection.cursor() as cursor:  # with语句用于数据库操作
            cursor.execute(sql)
            result_data = cursor.fetchall()
        result_list = []
        for i in result_data:
            result_list.append(i[0])
        result_dict = {'times': result_list}
        print(result_data)
        result_data = {
            "message": '成功',
            "code": 200,
            'data': result_dict,
        }
        return JsonResponse(result_data, json_dumps_params={'ensure_ascii': False},
                            content_type='application/json, charset=utf-8')


# 电力  电量 指标
def get_electricity_target(request):
    if request.method == 'POST':
        datatimes = request.POST.get('datatimes')  # 日期
        sql = """
        SELECT a.region, a.power_supply_lift, a.load_power, SUBSTR(a.datatimes,12), 
        b.power_coefficient,b.electric_coefficient from  
        power_supply_clean_data a INNER JOIN electrical_index_coefficient b 
        ON a.region = b.region AND a.datatimes =b.datetiming
        """

        with connection.cursor() as cursor:  # with语句用于数据库操作
            cursor.execute(sql)
            result_sql_data = cursor.fetchall()
        print(result_sql_data)
        result_sql_list = []
        for i in result_sql_data:
            result_sql_list.append({"region": i[0],
                                    "power_supply_lift": i[1],
                                    "load_power": i[2],
                                    "timing": i[3],
                                    "power_coefficient": i[4],
                                    "electric_coefficient": i[5],
                                    })
        df = pd.DataFrame(result_sql_list)
        result_list = []
        for i in send_timing:
            df1 = df[df['timing'] <= i]
            for region, df_region in df1.groupby('region'):
                df_region_timing = df_region[df_region['timing'] == i]
                result_list.append({
                    'region': region,
                    'power_supply_lift': df_region_timing['power_supply_lift'].to_list()[0],
                    'load_power': df_region_timing['load_power'].to_list()[0],
                    'power_coefficient': df_region_timing['power_coefficient'].to_list()[0],
                    'electric_coefficient': df_region_timing['electric_coefficient'].to_list()[0],
                    'power_supply_lift_quantity': round(df_region['power_supply_lift'].sum(), 2),
                    'load_power_quantity': round(df_region['load_power'].sum(), 2),
                    'timing': i,
                })

        print(result_list)
        result_data = {
            "message": '成功',
            "code": 200,
            'data': result_list,
        }
        return JsonResponse(result_data, json_dumps_params={'ensure_ascii': False},
                            content_type='application/json, charset=utf-8')


def get_electricity_target_timing(request):
    if request.method == 'POST':
        datatimes = request.POST.get('datatimes')  # 日期时间
        sql = f"""
        SELECT a.region, a.power_supply_lift, a.load_power, SUBSTR(a.datatimes,12), 
        b.power_coefficient,b.electric_coefficient from  
        power_supply_clean_data a INNER JOIN electrical_index_coefficient b 
        ON a.region = b.region AND a.datatimes =b.datetiming WHERE a.datatimes <= '{datatimes}'
        """
        with connection.cursor() as cursor:  # with语句用于数据库操作
            cursor.execute(sql)
            result_sql_data = cursor.fetchall()

        result_sql_list = []
        for i in result_sql_data:
            result_sql_list.append({"region": i[0],
                                    "power_supply_lift": i[1],
                                    "load_power": i[2],
                                    "timing": i[3],
                                    "power_coefficient": i[4],
                                    "electric_coefficient": i[5],
                                    })
        df = pd.DataFrame(result_sql_list)
        result_list = []
        for region, df_region in df.groupby('region'):
            df_region_timing = df_region[df_region['timing'] == datatimes[11:]]
            result_list.append({
                'region': region,
                'power_supply_lift': df_region_timing['power_supply_lift'].to_list()[0],
                'load_power': df_region_timing['load_power'].to_list()[0],
                'power_coefficient': df_region_timing['power_coefficient'].to_list()[0],
                'electric_coefficient': df_region_timing['electric_coefficient'].to_list()[0],
                'power_supply_lift_quantity': round(df_region['power_supply_lift'].sum(), 2),
                'load_power_quantity': round(df_region['load_power'].sum(), 2),
                'timing': datatimes,
            })
        result_data = {
            "message": '成功',
            "code": 200,
            'data': result_list,
        }
        return JsonResponse(result_data, json_dumps_params={'ensure_ascii': False},
                            content_type='application/json, charset=utf-8')


# 水/新能源
def get_clean_energy(request):
    if request.method == 'POST':
        datatimes = request.POST.get('datatimes')  # 日期
        flag = request.POST.get('flag')  # 标签 1 水   2 新能源
        if int(flag) == 1:
            fuel = 'white_fuel'
            fuel_to = 'white_fuel_to'
            power_coefficient = 'water_power_coefficient'
            electric_coefficient = 'water_electric_coefficient'
        else:
            fuel = 'new_energy'
            fuel_to = 'new_energy_to'
            power_coefficient = 'new_energy_power_coefficient'
            electric_coefficient = 'new_energy_electric_coefficient'
        sql = f"""
        SELECT a.region, a.{fuel}, a.{fuel_to}, SUBSTR(a.datatimes,12), 
        b.{power_coefficient},b.{electric_coefficient} from  
        power_supply_clean_data a INNER JOIN electrical_index_coefficient b 
        ON a.region = b.region AND a.datatimes =b.datetiming
        """
        print(sql)

        with connection.cursor() as cursor:  # with语句用于数据库操作
            cursor.execute(sql)
            result_sql_data = cursor.fetchall()
        print(result_sql_data)
        result_sql_list = []
        for i in result_sql_data:
            result_sql_list.append({"region": i[0],
                                    "fuel": i[1],
                                    "fuel_to": i[2],
                                    "timing": i[3],
                                    "power_coefficient": i[4],
                                    "electric_coefficient": i[5],
                                    })

        df = pd.DataFrame(result_sql_list)
        result_list = []

        for i in send_timing:
            df1 = df[df['timing'] <= i]
            for region, df_region in df1.groupby('region'):
                df_region_timing = df_region[df_region['timing'] == i]

                result_list.append({
                    'region': region,
                    'fuel': df_region_timing['fuel'].to_list()[0],
                    'fuel_to': df_region_timing['fuel_to'].to_list()[0],
                    'power_coefficient': df_region_timing['power_coefficient'].to_list()[0],
                    'electric_coefficient': df_region_timing['electric_coefficient'].to_list()[0],
                    'fuel_quantity': round(df_region['fuel'].sum(), 2),
                    'fuel_to_quantity': round(df_region['fuel_to'].sum(), 2),
                    'timing': i,
                })

        print(result_list)
        result_data = {
            "message": '成功',
            "code": 200,
            'data': result_list,
        }
        return JsonResponse(result_data, json_dumps_params={'ensure_ascii': False},
                            content_type='application/json, charset=utf-8')


# 水/新能源--时间点查询
def get_clean_energy_timing(request):
    if request.method == 'POST':
        datatimes = request.POST.get('datatimes')  # 日期
        flag = request.POST.get('flag')  # 标签 1 水   2 新能源
        if int(flag) == 1:
            fuel = 'white_fuel'
            fuel_to = 'white_fuel_to'
            power_coefficient = 'water_power_coefficient'
            electric_coefficient = 'water_electric_coefficient'
        else:
            fuel = 'new_energy'
            fuel_to = 'new_energy_to'
            power_coefficient = 'new_energy_power_coefficient'
            electric_coefficient = 'new_energy_electric_coefficient'
        sql = f"""
        SELECT a.region, a.{fuel}, a.{fuel_to}, SUBSTR(a.datatimes,12), 
        b.{power_coefficient},b.{electric_coefficient} from  
        power_supply_clean_data a INNER JOIN electrical_index_coefficient b 
        ON a.region = b.region AND a.datatimes =b.datetiming where a.datatimes <= '{datatimes}'
        """
        print(sql)
        with connection.cursor() as cursor:  # with语句用于数据库操作
            cursor.execute(sql)
            result_sql_data = cursor.fetchall()
        print(result_sql_data)
        result_sql_list = []
        for i in result_sql_data:
            result_sql_list.append({"region": i[0],
                                    "fuel": i[1],
                                    "fuel_to": i[2],
                                    'timing': i[3],
                                    "power_coefficient": i[4],
                                    "electric_coefficient": i[5],
                                    })

        df = pd.DataFrame(result_sql_list)
        result_list = []

        for region, df_region in df.groupby('region'):
            df_region_timing = df_region[df_region['timing'] == datatimes[11:]]
            result_list.append({
                'region': region,
                'fuel': df_region_timing['fuel_to'].to_list()[0],
                'fuel_to': df_region_timing['fuel_to'].to_list()[0],
                'power_coefficient': df_region_timing['power_coefficient'].to_list()[0],
                'electric_coefficient': df_region_timing['electric_coefficient'].to_list()[0],
                'fuel_quantity': round(df_region['fuel'].sum(), 2),
                'fuel_to_quantity': round(df_region['fuel_to'].sum(), 2),
                'timing': datatimes[11:],
            })

        print(result_list)
        result_data = {
            "message": '成功',
            "code": 200,
            'data': result_list,
        }
        return JsonResponse(result_data, json_dumps_params={'ensure_ascii': False},
                            content_type='application/json, charset=utf-8')


# 综合调节能力指标 省网 和区域电网
def get_region_target(request):
    if request.method == 'POST':
        datatimes = request.POST.get('datatimes')  # 日期
        sql = """
        SELECT region, synthesize_target, SUBSTR(datatimes,12) from  synthesize_target_data
        """

        with connection.cursor() as cursor:  # with语句用于数据库操作
            cursor.execute(sql)
            result_sql_data = cursor.fetchall()
        print(result_sql_data)
        result_sql_list = []
        for i in result_sql_data:
            result_sql_list.append({"region": i[0],
                                    "synthesize_target": i[1],
                                    "timing": i[2],
                                    })
        df = pd.DataFrame(result_sql_list)
        df1 = df[df['timing'].isin(send_timing)]
        result_list = df1.to_dict(orient='records')
        print(result_list)
        result_data = {
            "message": '成功',
            "code": 200,
            'data': result_list,
        }
        return JsonResponse(result_data, json_dumps_params={'ensure_ascii': False},
                            content_type='application/json, charset=utf-8')


# 综合调节能力指标时间点查询
def get_synthesize_target(request):
    if request.method == 'POST':
        datatimes = request.POST.get('datatimes')  # 日期时间
        sql = f"""
        SELECT region, synthesize_target from  synthesize_target_data
        where datatimes = '{datatimes}'
        """
        with connection.cursor() as cursor:  # with语句用于数据库操作
            cursor.execute(sql)
            result_sql_data = cursor.fetchall()

        result_sql_list = []
        for i in result_sql_data:
            result_sql_list.append({"region": i[0],
                                    "synthesize_target": i[1],
                                    })
        result_data = {
            "message": '成功',
            "code": 200,
            'data': result_sql_list,
        }
        return JsonResponse(result_data, json_dumps_params={'ensure_ascii': False},
                            content_type='application/json, charset=utf-8')
