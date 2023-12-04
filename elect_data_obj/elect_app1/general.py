import pandas as pd
from django.db import connection


def elect_start_data(district, region, datatimes):
    if district:
        sql = f"""SELECT a.region, a.district, b.fire_generation,b.water_generation,b.take_generation, b.wind_generation,
             b.light_generation,b.receive_generation, b.timing
            FROM (SELECT * FROM region_district WHERE region = '{region}' and district = '{district}') a	
            INNER JOIN electric_satrt_sum_data b ON a.district = b.district
            """

    else:
        sql = f"""SELECT a.region,'', sum(b.fire_generation), sum(b.water_generation),
            sum(b.take_generation), sum(b.wind_generation), sum(b.light_generation),sum(b.receive_generation), b.timing
            FROM (SELECT * FROM region_district WHERE region = '{region}') a	
            INNER JOIN electric_satrt_sum_data b ON a.district = b.district group by b.datatimes, b.timing
            """
    print(sql)
    with connection.cursor() as cursor:  # with语句用于数据库操作
        cursor.execute(sql)
        result_data = cursor.fetchall()
    print(result_data)
    result_list = []
    for a in result_data:
        result_list.append({
            'region': a[0],
            'district': a[1],
            'fire_generation': delete_extra_zero(a[2]),
            'water_generation': delete_extra_zero(a[3]),
            'take_generation': delete_extra_zero(a[4]),
            'wind_generation': delete_extra_zero(a[5]),
            'light_generation': delete_extra_zero(a[6]),
            'receive_generation': delete_extra_zero(a[7]),
            'timing': a[8]})
    df = pd.DataFrame(result_list)
    return df, result_list


def fracture_data(flag, datatimes):
    sql = f"""SELECT cast( member1+ member2+ member3 AS DECIMAL (19, 2) )  AS member,datatimes,timing from
             region_exchange_power where flag = {flag}
    	     """
    with connection.cursor() as cursor:  # with语句用于数据库操作
        cursor.execute(sql)
        exchange_power_data = cursor.fetchall()
    print(exchange_power_data)
    result_list = []
    for a in exchange_power_data:
        result_list.append({'fracture_data': delete_extra_zero(a[0]),
                            'timing': a[2]})
    df1 = pd.DataFrame(result_list)
    return df1, result_list


def result_count_data(district, flag, region, datatimes):
    if district:
        sql = f"""SELECT a.region,  a.district, ifnull(b.fire_quantity, 0), ifnull(b.water_quantity, 0),
                ifnull(b.take_quantity, 0), ifnull(b.wind_quantity, 0), ifnull(b.light_quantity, 0), b.timing 
            FROM
                ( SELECT * FROM region_district WHERE region = '{region}' AND district = '{district}' ) a
                INNER JOIN (SELECT * from result_quantity WHERE flag = {flag}) b ON a.district = b.district;
            """

    else:
        sql = f"""SELECT a.region, '',
                ifnull(cast( sum( b.fire_quantity ) AS DECIMAL ( 19, 2 )),0 )AS fire_quantity,
                ifnull(cast( sum( b.water_quantity ) AS DECIMAL ( 19, 2 )),0) AS water_quantity,
                ifnull(cast( sum( b.take_quantity ) AS DECIMAL ( 19, 2 )),0 ) AS take_quantity,
                ifnull(cast( sum( b.wind_quantity ) AS DECIMAL ( 19, 2 )),0 ) AS wind_quantity,
                ifnull(cast( sum( b.light_quantity ) AS DECIMAL ( 19, 2 )),0 ) AS light_quantity,
                b.timing 
            FROM
                ( SELECT * FROM region_district WHERE region = '{region}' ) a
                INNER JOIN (SELECT * from result_quantity WHERE flag = {flag}) b ON a.district = b.district 
            GROUP BY
                b.datatimes,
                b.timing;
            """
    print(sql)
    with connection.cursor() as cursor:  # with语句用于数据库操作
        cursor.execute(sql)
        result_data = cursor.fetchall()
    print(result_data)
    sql2 = f"""
        SELECT load_power from load_quantity WHERE flag = {flag} AND degion='{region}'
        """
    print(sql2)
    with connection.cursor() as cursor:  # with语句用于数据库操作
        cursor.execute(sql2)
        load_data = cursor.fetchall()
    print(load_data)
    result_list = []
    for a, b in zip(result_data, load_data):
        result_list.append({
            'region': a[0],
            'district': a[1],
            'fire_quantity': delete_extra_zero(a[2]),
            'water_quantity': delete_extra_zero(a[3]),
            'take_quantity': delete_extra_zero(a[4]),
            'wind_quantity': delete_extra_zero(a[5]),
            'light_quantity': delete_extra_zero(a[6]),
            'load_power': delete_extra_zero(b[0]),
            'timing': a[7]})
    df1 = pd.DataFrame(result_list)
    return df1, result_list


def take_quantity(district, flag, region, datatimes):
    if district:
        sql = f"""
            SELECT a.area_name, a.area_generated, a.timing from 
            (SELECT area_name, area_generated, timing  from take_area_generated WHERE flag = {flag})a
            INNER JOIN (SELECT * from region_district WHERE region='{region}' AND district = '{district}')b 
            ON a.area_name = b.area_down
            """
    else:
        sql = f"""
            SELECT b.region, sum(a.area_generated), a.timing from 
            (SELECT area_name, area_generated, timing  from take_area_generated WHERE flag = {flag})a
            INNER JOIN (SELECT * from region_district WHERE region='{region}')b ON a.area_name = b.area_down 
            GROUP BY a.timing
            """
    print(sql)
    with connection.cursor() as cursor:  # with语句用于数据库操作
        cursor.execute(sql)
        result_data = cursor.fetchall()
    print(result_data)
    result_list = []
    for a in result_data:
        result_list.append({
            "region": a[0],
            "take_quantity": a[1],
            "timing": a[2],
        })
    df = pd.DataFrame(result_list)
    return df, result_list


def delete_extra_zero(m):
    """删除小数点后多余的0"""
    n = str(m)
    if '.' in n:
        n = n.rstrip('0')  # 删除小数点后多余的0
        n = int(n.rstrip('.')) if n.endswith('.') else float(n)  # 只剩小数点直接转int，否则转回float
    else:
        return m
    return n


def region_all_data(data, region):
    data_dict = {}
    data_dict.update({'fire_generation': data[0][0]})
    data_dict.update({'water_generation': data[0][1]})
    data_dict.update({'take_generation': data[0][2]})
    data_dict.update({'wind_generation': data[0][3]})
    data_dict.update({'light_generation': data[0][4]})
    data_all_dict = {region: data_dict}
    return data_all_dict


def sum_data(data, data_name):
    result_list2 = []
    for i in data:
        l_dict = {'region': i[0], 'data': i[1]}
        result_list2.append(l_dict)
    return {data_name: result_list2}
