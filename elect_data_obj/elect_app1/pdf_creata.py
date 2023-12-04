import matplotlib
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker

matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

plt.rcParams['xtick.direction'] = 'in'
plt.rcParams['ytick.direction'] = 'in'

# 电源数据图
"""
左 ：generation
右 ：quantity
"""


def left_start_png(df, claasses, png_name):
    df['times'] = df['timing'].apply(lambda x: x[:-3])
    times = df['times']
    m1 = df['fire_' + claasses]
    m2 = df['water_' + claasses]
    m3 = df['take_' + claasses]
    m4 = df['wind_' + claasses]
    m5 = df['light_' + claasses]

    plt.figure()
    # label指定图例，即右上角的指示
    plt.bar(times, m1, label="火电发电")
    plt.bar(times, m2, label="水电发电")
    plt.bar(times, m3, label="抽蓄发电")
    plt.bar(times, m4, label="风电发电")
    plt.bar(times, m5, label="光电发电")

    plt.xticks(fontsize=6)
    plt.xlabel('时间间隔5分钟')
    plt.ylabel('发电')
    plt.legend(loc='upper right')
    ax = plt.gca()
    # X轴间隔为8
    ax.xaxis.set_major_locator(ticker.MultipleLocator(8))
    plt.savefig(png_name)


# 左--负荷数据图
"""
左
负荷： receive_generation， 负荷， left_load.png
储能 ： take_generation， 储能， left_take.png
断面 ：fracture_data, 断面， fracture.png

右
负荷 ： load_power， 负荷， right_load.png
储能--发电功率 ： take_quantity， 储能--发电功率， right_take_power.png
"""


# 单线的折线图
def plot_png(df, df_col, y_name, png_name):
    try:
        df['times'] = df['timing'].apply(lambda x: x[:-3])
    except Exception as e:
        return ''
    times = df['times']
    m1 = df[df_col]

    plt.figure()
    plt.plot(times, m1, label='second line')
    plt.xticks(fontsize=6)
    plt.ylabel(y_name)

    ax = plt.gca()
    # X轴间隔为8
    ax.xaxis.set_major_locator(ticker.MultipleLocator(8))
    plt.savefig(png_name)


# 右 电量
def right_take_quantity(df, png_name):
    try:
        df['times'] = df['timing'].apply(lambda x: x[:-3])
    except Exception as e:
        return ''
    times = df['times']
    region_list = df['region'].to_list()
    region_set = set(region_list)
    region_len = len(region_set)
    plt.figure()
    if region_len == 1:
        m1 = df['take_quantity']
        plt.plot(times, m1, label='second line')
        plt.xticks(fontsize=6)
    else:
        for i in region_set:
            m1 = df[df['region'] == i]['take_quantity'].to_list()
            times = df[df['region'] == i]['times'].to_list()
            plt.plot(times, m1, label='second line')
            plt.xticks(fontsize=6)
    plt.legend(region_set)
    ax = plt.gca()
    # X轴间隔为8
    ax.xaxis.set_major_locator(ticker.MultipleLocator(8))
    plt.savefig(png_name)
