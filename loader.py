# -*- coding: UTF-8 -*-
import pandas as pd

def load_config() :
    units_f = []
    units_b = {}
    quotas_f = []
    quotas_n = {}
    quotas_b = {}
    unit_file = open('unit.config')
    quota_file = open('quota.config')
    id = 0
    for line in unit_file :
        unit = line.strip()
        units_b[unit] = id
        units_f.append(unit)
        id += 1
    id = 0
    for line in quota_file :
        (quota, note) = line.strip().split(',')
        quotas_b[quota] = id
        quotas_f.append(quota)
        quotas_n[quota] = note
        id += 1
    return (units_f, units_b, quotas_f, quotas_b, quotas_n)

def load_excel(file_name) :
    sheet = pd.read_excel(file_name, header=1)
    values = sheet.values
    unit_name = values[0][1]
    report_time = values[1][1]
    year = report_time.split('年')[0]
    season = report_time.split('年')[1].split('月')[0]
    datas = []
    for data in values[3:-1] :
        datas.append((data[0],data[1]))
    return (unit_name, year, season, datas)