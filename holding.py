import requests
import xml.etree.ElementTree as ET
from lxml import etree
from bs4 import BeautifulSoup
import json
import csv
import re
import time
import operator
import os
from datetime import datetime
import xlrd
from decimal import Decimal
from itertools import zip_longest

starttime = datetime.now()

class Comparexml:
    def __init__(self):
        self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36'}
        self.holdingcsv_filepath = r'D:\ms\holding_debug.csv'


    def get_white(self):
        '''
        获取白名单 ISIN==MS_SECID
        '''
        id = []
        with open('IE.txt', 'r', encoding='utf-8')as f:
            for x in f.readlines():
                id.append(x.replace('\n', ''))
        return id


    def get_time(self):
        times = time.strftime("%Y%m%d%H%MS", time.localtime())
        return times


    def date_conversion(self,csv_managerStartDate):# 日期转换：xml中日期格式xxxx-xx-xx,  csv中日期格式xxxx/xx/xx
        csv_year = csv_managerStartDate[0]  # 年
        csv_month = csv_managerStartDate[1]  # 月
        csv_day = csv_managerStartDate[2]  # 日
        if len(csv_month) == 1:  # 如果月的长度为1
            csv_month = f'0{csv_month}'
        if len(csv_day) == 1:  # 如果日的长度为1
            csv_day = f'0{csv_day}'
        start_date = f"{csv_year}-{csv_month}-{csv_day}"  # 生成新的日期格式xxxx-xx-xx
        return start_date


    def write_compare_data(self, dirpath_name, cons, times):
        '''
        将比较后的结果写入txt
        '''
        pwd = os.getcwd()
        dirpath = os.path.join(pwd, dirpath_name)
        compare_result_txt = os.path.exists(dirpath)
        if not compare_result_txt:
            with open(f'{dirpath_name}{times}.txt', 'a+', encoding='utf-8')as f:
                f.write(f'{cons}\n')
        else:
            with open(f'{dirpath_name}{times}.txt', 'a+', encoding='utf-8')as f:
                f.write(f'{cons}\n')


    def xml_holding(self):
        new_xml_list = []
        id_list = self.get_white()
        for m in id_list:
            xml_list = []
            m = m.split('==')
            ISIN = m[0]
            MS_SECID = m[1]

            # url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"

            url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnum2022&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS&Obsolete=1 "
            res = requests.get(url)

            if res.status_code == 200:
                print(f">>>>>>>>>>开始获取'{MS_SECID}'的数据>>>>>>>>>>")
                xml_holding_text = res.text
                xml_holding = re.findall('<Holding>(.*?)</Holding>', xml_holding_text, re.S)  # 修饰符re.S  使.匹配包括换行在内的所有字符
                # reportDate在其他位置
                xml_holding_date = re.findall("<PortfolioSummary>(.*?)</PortfolioSummary>", xml_holding_text, re.S)
                if xml_holding_date:
                    holding_list_date = xml_holding_date[0]
                    holding_detail_date = re.findall("<Date>(.*?)</Date>", holding_list_date)
                    if holding_detail_date:
                        print(f"reportDate : {holding_detail_date[0]}")
                if xml_holding:
                    # 获取holdingISINCode,securityName,weight
                    holding_list = xml_holding[0]
                    holding_detail = holding_list.split("</HoldingDetail>")

                    weight_list_detail = []
                    l = []
                    ll = []
                    weight_list = []
                    # 遍历序列中的元素及其下标
                    for num, hd in enumerate(holding_detail):
                        xml_list_detail = []
                        xml_dic_detail = {}
                        weight_dic = {}
                        xml_list_detail_2 = []
                        w_list = []
                        dic_detail = []
                        Weighting = re.findall("<Weighting>(.*?)</Weighting>", hd)
                        if Weighting:
                            # print(f"Weighting", Weighting[0])
                            weight_text = str((Decimal(Weighting[0]) / 100).quantize(Decimal('0.000000'), rounding='ROUND_HALF_UP')).rstrip("0")
                            weight_float = float(weight_text)
                            # 持仓占比
                            xml_list_detail.append(ISIN)
                            isin_code = re.findall("<ISIN>(.*?)</ISIN>", hd)
                            if isin_code:
                                # print(isin_code[0])
                                xml_list_detail.append(isin_code[0])
                            else:
                                pass
                            #     xml_list_detail.append("")
                            currency = re.findall('<Currency _Id="(.*?)">',hd)
                            if currency:
                                # print(currency[0])
                                xml_list_detail.append(currency[0])
                            else:
                                pass
                            security_name = re.findall("<SecurityName>(.*?)</SecurityName>", hd)
                            if security_name:
                                xml_list_detail.append(security_name[0])

                            xml_list_detail.append(holding_detail_date[0])
                            xml_list_detail.sort()
                            xml_list_detail.append(weight_float)
                            l.append(xml_list_detail)

                            nw = {}
                            sum_list = []
                            for x in l:
                                key = tuple(x[:-1])
                                nw[key] = [i + j for i, j in zip_longest(nw.get(key, []), x[-1:], fillvalue=0)]

                            sum_v = []
                            for k, v in nw.items():
                                k = list(k)
                                sum_list.append(k)
                                k.append(str(v[0]))
                                sum_v.append(v[0])

                            ll = sum_list

                            for i, j in enumerate(ll):
                                xml_dic_detail[i] = j
                            dic_detail.append(xml_dic_detail)
                            xml_list = dic_detail

                            for ii, jj in enumerate(sum_v):
                                weight_dic[ii] = jj
                            w_list.append(weight_dic)
                            weight_list = w_list
                            # print("================================")
                    sum_v = sorted(sum_v, key=float, reverse=True)
                    weight_num_list = self.get_weight_num(sum_v, weight_list)
                    print(f"排序后的weight坐标: {weight_num_list}")
                    # 根据新坐标获取列表
                    for wl in weight_num_list[:10]:
                        for xxx in xml_list:
                            for k, v in xxx.items():
                                if wl == k:
                                    new_xml_list.append(v)
                # print(f"new_xml_list:", new_xml_list)
                for i in new_xml_list:
                    i = i.sort()
                print(new_xml_list)
        return new_xml_list


    def get_weight_num(self,sum_v, weight_list):
        """
        获取weight从大到小的坐标
        :return:
        """
        new_weight_num = []
        for wd in sum_v:
            for xx in weight_list:
                for k, v in xx.items():
                    if wd == v:
                        new_weight_num.append(k)
        return new_weight_num


    def read_holding_csv(self):
        holding_csv_dic = {}
        with open(self.holdingcsv_filepath, 'r') as f:
            reader = csv.reader(f)
            i = 0
            for row in reader:
                if i == 0:
                    pass
                else:
                    row = row[0:6]
                    report_date = row[5]  # 读取csv中的日期
                    if "/" in report_date:
                        csv_reportDate = report_date.split("/")  # csv中，年月日，根据"/"切割
                        report_date = self.date_conversion(csv_reportDate)  # 把切割后的列表传进日期转换的方法date_conversion()
                    if "-" in report_date: # 同理，月份1~9加0，日期1~9加0
                        csv_reportDate = report_date.split("-")
                        report_date = self.date_conversion(csv_reportDate)
                    row[5] = report_date
                    row.sort()
                    while "" in row:
                        row.remove("")
                    holding_csv_dic[f"第{i}行"] = row
                i += 1
            print(holding_csv_dic)
            return holding_csv_dic


    def compare_holding(self):
        '''
        比较 holding.csv文件
        '''
        times = self.get_time()
        print('\n>>>>>>>>>>正在比较holding.csv文件>>>>>>>>>>')
        holding_list = self.xml_holding()
        # print(holding_list)
        print(f"ms数据量：",len(holding_list))
        csv_data = self.read_holding_csv()
        # print(csv_data)
        print(f"holding.csv数据量：",len(csv_data))

        if len(holding_list) == len(csv_data):
            j = 0
            for k, v in csv_data.items():
                i = 0
                for cm in holding_list:
                    if operator.eq(cm, v):
                        i += 1
                        j += 1
                    else:
                        pass
                # i += 1 # 打印相同数据
                if i != 1:# 数据相同，i计数+1,即相同的数据不写入txt
                    self.write_compare_data('result_holding.txt', k, times)
                    print(f'数据不一致：',k)
            if j == len(holding_list):# 数据比对相同时，j的计数+1，相同数=总数，数据一致。
                print('\nholding.csv >>>校验通过，数据一致!')
        else:
            print('数据量不一致')
            self.write_compare_data('result_manager.txt', '数据量不一致', times)



if __name__ == '__main__':
    c = Comparexml()

    # # 校验holding.csv
    c.compare_holding()

    endtime = datetime.now()
    print("RunTime: {}h-{}m-{}s".format(endtime.hour-starttime.hour, endtime.minute-starttime.minute, endtime.second-starttime.second))