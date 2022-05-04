# -*- coding: utf-8 -*-
# @Time    : 2022/5/4 16:30
# @FileName: charts.py
# @Author  : CNPolaris
from django.http import JsonResponse, HttpResponse
import json
import datetime
from . import models

PROVINCE_CODES = {
    "黑龙江": "HLJ",
    "香港": "XG",
    "青海": "QH",
    "陕西": "SX",  # 同山西
    "重庆": "CQ",
    "辽宁": "LN",
    "贵州": "GZ",
    "西藏": "XZ",
    "福建": "FJ",
    "甘肃": "GS",
    "澳门": "AM",
    "湖南": "HN",
    "湖北": "HB",
    "海南": "HN-2",
    "浙江": "ZJ",
    "河南": "HN-1",
    "河北": "HB-1",
    "江西": "JX",
    "江苏": "JS",
    "新疆": "XJ",
    "广西": "GX",
    "广东": "GD",
    "山西": "SX-1",
    "山东": "SD",
    "安徽": "AH",
    "宁夏": "NX",
    "天津": "TJ",
    "四川": "SC",
    "吉林": "JL",
    "台湾": "TW",
    "北京": "BJ",
    "内蒙古": "NMG",
    "云南": "YN",
    "上海": "SH"
}

PROVINCE_RESPONSE = {
    "HLJ": 0,
    "XG": 0,
    "QH": 0,
    "SX": 0,
    "CQ": 0,
    "LN": 0,
    "XZ": 0,
    "FJ": 0,
    "GS": 0,
    "AM": 0,
    "HN": 0,
    "HB": 0,
    "HN-2": 0,
    "ZJ": 0,
    "HN-1": 0,
    "HB-1": 0,
    "JX": 0,
    "JS": 0,
    "XJ": 0,
    "GX": 0,
    "GD": 0,
    "SX-1": 0,
    "SD": 0,
    "AH": 0,
    "NX": 0,
    "TJ": 0,
    "SC": 0,
    "JL": 0,
    "TW": 0,
    "BJ": 0,
    "NMG": 0,
    "YN": 0,
    "SH": 0
}


def GetProvinceDayList(request):
    """统计各省今日新增人数"""
    date = datetime.datetime.now().strftime("%Y%m%d")
    querySet = models.Province.objects.order_by('provinceCode')
    result = []
    for item in querySet.values():
        dailyData = json.loads(item['dailyData'])
        if dailyData is not None:
            for d in dailyData:
                if d['dateId'] == 20220503:
                    result.append(d)
    confirmed = {}
    cured = {}
    dead = {}
    for item in result:
        confirmed[item['provinceCode']] = item['confirmedCount']
        cured[item['provinceCode']] = item['curedCount']
        dead[item['provinceCode']] = item['deadCount']
    confirmedCount = []
    curedCount = []
    deadCount = []
    for key in PROVINCE_RESPONSE.keys():
        confirmedCount.append(confirmed[key])
        curedCount.append(confirmed[key])
        deadCount.append(dead[key])

    response = {'confirmedCount': confirmedCount, 'curedCount': curedCount, 'deadCount': deadCount,
                'province': list(PROVINCE_CODES.keys())}
    return HttpResponse(json.dumps(response), content_type='application/json')
