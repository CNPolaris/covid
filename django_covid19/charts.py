# -*- coding: utf-8 -*-
# @Time    : 2022/5/4 16:30
# @FileName: charts.py
# @Author  : CNPolaris
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.db import connection
import requests
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


def CumulateInfo(request):
    """
    昨日全国累计疫情
    :param request: get
    :return: Json
    """
    confirmedCount = models.Province.objects.filter(countryCode='CHN').aggregate(total=Sum("confirmedCount"))['total']
    curedCount = models.Province.objects.filter(countryCode='CHN').aggregate(total=Sum("curedCount"))['total']
    deadCount = models.Province.objects.filter(countryCode='CHN').aggregate(total=Sum("deadCount"))['total']
    response = {"confirmedCount": confirmedCount, "curedCount": curedCount, "deadCount": deadCount}
    return HttpResponse(json.dumps(response),content_type='application/json')


def GetChinaCumulateConfirmed(request):
    """
    获取全国累计确诊疫情趋势
    :param request:Get
    :return:Json
    """
    confirmed = {}
    cured = {}
    dead = {}
    for key in PROVINCE_RESPONSE.keys():
        querySet = models.Province.objects.filter(provinceCode=key, countryCode='CHN')
        for item in querySet.values():
            dailyData = json.loads(item['dailyData'])
            if dailyData is not None:
                dailyData = dailyData[-30:]
                for date in dailyData:
                    # 日期
                    d = datetime.datetime.strptime(str(date['dateId']),'%Y%m%d').date().strftime('%Y-%m-%d')
                    # 累计确诊
                    if d in confirmed.keys():
                        confirmed[d] = confirmed[d] + date['confirmedCount']
                    else:
                        confirmed[d] = date['confirmedCount']
                    # 累计治愈
                    if d in cured.keys():
                        cured[d] = cured[d] + date['curedCount']
                    else:
                        cured[d] = date['curedCount']
                    # 累计死亡
                    if d in dead.keys():
                        dead[d] = dead[d] + date['deadCount']
                    else:
                        dead[d] = date['deadCount']

    return HttpResponse(json.dumps({"date":list(confirmed.keys()),"confirmed":list(confirmed.values()),"cured":list(cured.values()),"dead": list(dead.values())}), content_type='application/json')


def GetProvinceDayList(request):
    """统计各省今日新增人数"""
    date = datetime.datetime.now().strftime("%Y%m%d")
    querySet = models.Province.objects.filter(countryCode='CHN').order_by('provinceCode')
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


def GetYourCountryCovidInfo(request):
    """
    根据访问ip信息获取所属国家的疫情信息
    :param request:
    :return: json
    """
    code = request.GET.get('provinceCode')
    querySet = models.Province.objects.filter(provinceCode=code)
    dailyData = {}
    provinceConfirmed = 0
    provinceDead = 0
    for item in querySet.values():
        dailyData = json.loads(item['dailyData'])[-1]
        provinceConfirmed = item['confirmedCount']
        provinceDead = item['deadCount']
    return HttpResponse(json.dumps({"dailyData":dailyData,"provinceConfirmed":provinceConfirmed,"provinceDead":provinceDead}),content_type='application/json')


def GetChinaCountry(request):
    """
    中国趋势
    :param request:
    :return:
    """
    confirmed = {}
    cured = {}
    dead = {}
    session = requests.session()
    session.trust_env = False
    re = session.get("https://jz-forecast.oss-cn-beijing.aliyuncs.com/data/by_overall.json")
    records = json.loads(re.text)[0].get('records')
    return HttpResponse(json.dumps({"records": records}),content_type="application/json")


def GetProvinceDaily(request):
    """
    获取各省的日统计
    :param request:
    :return:
    """
    date = []
    confirmed = []
    dead = []
    code = request.GET.get('provinceCode')
    querySet = models.Province.objects.filter(provinceCode=code)
    for item in querySet.values():
        dailyData = json.loads(item['dailyData'])
        for d in dailyData:
            date.append(d['dateId'])
            confirmed.append(d['confirmedCount'])
            dead.append(d['deadCount'])
    return HttpResponse(json.dumps({"date":date, "confirmed": confirmed,"dead":dead}), content_type="application/json")


def GetNowProvince(request):
    """
    获取各省的新增
    :param request:
    :return:
    """
    session = requests.session()
    session.trust_env = False
    re = session.get("https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=chinaDayList,chinaDayAddList,nowConfirmStatis,provinceCompare")
    response = json.loads(re.text).get('data').get('provinceCompare')
    return HttpResponse(json.dumps({"provinceCompare": response}),content_type="application/json")


def GetEveryProvince(request):
    """
    获取各省市的数据
    :param request:
    :return:
    """
    session = requests.session()
    session.trust_env = False
    re = session.get("https://jz-forecast.oss-cn-beijing.aliyuncs.com/data/by_area.json")
    response = json.loads(re.text)
    return HttpResponse(json.dumps({"provinces": response}), content_type='application/json')