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


starttime = datetime.now()
print(starttime)

class Comparexml:
    def __init__(self):
        self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36'}
        self.market_filepath = r'D:\ms\csv\market_debug.csv'
        self.white_filepath = r'D:\ms\white\white_v6.xlsx'


    def get_white(self):
        '''
        获取白名单 ISIN==MS_SECID
        '''
        id = []
        with open('D:\ms\white\white_debug.txt', 'r', encoding='utf-8')as f:
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


    def read_xlsx(self):
        workbook = xlrd.open_workbook(self.white_filepath)
        Data_sheet = workbook.sheets()[0]  # 通过索引获取
        rowNum = Data_sheet.nrows  # sheet行数
        colNum = Data_sheet.ncols  # sheet列数
        xlsx_list = []

        region_dic = {}
        fundIndustry_dic = {}
        fundInvestType_dic = {}

        for i in range(1, rowNum):
            white_list = []
            for j in range(colNum):
                white_list.append(Data_sheet.cell_value(i, j))
            region_dic[white_list[4]] = white_list[-1]
            fundIndustry_dic[white_list[4]] = white_list[-2]
            fundInvestType_dic[white_list[4]] = white_list[-3]

        # 基金类型  1-股票型  2-债券型  3-货币型  4-混合型  8-另类投资型
        for k, v in fundInvestType_dic.items():
            if fundInvestType_dic[k] == '股票型':
                fundInvestType_dic[k] = "1"
            elif fundInvestType_dic[k] == '债券型':
                fundInvestType_dic[k] = "2"
            elif fundInvestType_dic[k] == '货币型':
                fundInvestType_dic[k] = "3"
            elif fundInvestType_dic[k] == '混合型':
                fundInvestType_dic[k] = "4"
            else:
                fundInvestType_dic[k] = "8"
        # print('\n基金类型_basicinfo:\n\t', fundInvestType_dic)
        xlsx_list.append(fundInvestType_dic)

        # 基金地域  0-无地区偏好  10-亚太市场  11-中国市场  21-美国市场  30-欧洲市场  70-新兴市场  90-全球市场
        for k, v in region_dic.items():
            if region_dic[k] == "亚太":
                region_dic[k] = "10"
            elif region_dic[k] == "中国":
                region_dic[k] = "11"
            elif region_dic[k] == "美国":
                region_dic[k] = "21"
            elif region_dic[k] == "欧洲":
                region_dic[k] = "30"
            elif region_dic[k] == "新兴":
                region_dic[k] = "70"
            elif region_dic[k] == "全球":
                region_dic[k] = "90"
            elif region_dic[k] == "其他":
                region_dic[k] = "0"
            else:
                region_dic[k] = ""
        # print('地区分类_basicinfo:\n\t', region_dic)
        xlsx_list.append(region_dic)

        # 0-无行业偏好  1-科技  2-消费  3-医疗  4-金融  5-工业  6-房地产  7-公用事业  8-能源  9-通信  10-基础材料
        for k, v in fundIndustry_dic.items():
            if fundIndustry_dic[k] == "科技":
                fundIndustry_dic[k] = "1"
            elif fundIndustry_dic[k] == "消费":
                fundIndustry_dic[k] = "2"
            elif fundIndustry_dic[k] == "医疗":
                fundIndustry_dic[k] = "3"
            elif fundIndustry_dic[k] == "金融":
                fundIndustry_dic[k] = "4"
            elif fundIndustry_dic[k] == "工业":
                fundIndustry_dic[k] = "5"
            elif fundIndustry_dic[k] == "房地产":
                fundIndustry_dic[k] = "6"
            elif fundIndustry_dic[k] == "公用事业":
                fundIndustry_dic[k] = "7"
            elif fundIndustry_dic[k] == "能源":
                fundIndustry_dic[k] = "8"
            elif fundIndustry_dic[k] == "通信":
                fundIndustry_dic[k] = "9"
            elif fundIndustry_dic[k] == "基础材料":
                fundIndustry_dic[k] = "10"
            elif fundIndustry_dic[k] == "其他":
                fundIndustry_dic[k] = "0"
            else:
                fundIndustry_dic[k] = ""
        # print('行业分类_basicinfo:\n\t', fundIndustry_dic)
        xlsx_list.append(fundIndustry_dic)

        # print(f'\nxlsx_list:\n\t',xlsx_list)
        return xlsx_list


    def get_PerformanceId(self):

        PerformanceId_list = []
        id_list = self.get_white()
        for m in id_list:
            m = m.split('==')
            ISIN = m[0]
            MS_SECID = m[1]

            url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"
            res = requests.get(url=url, headers=self.headers)
            data = requests.get(url=url, headers=self.headers)
            selector = etree.XML(data.content)
            pid_dict = {}
            if res.status_code == 200:
                print(f">>>>>>>>>>开始获取'{MS_SECID}'的PerformanceId>>>>>>>>>>")
                xml_market = res.text
                if xml_market:
                    xml_PerformanceId = selector.xpath(f"/FundShareClass/PerformanceId/Result/PerformanceId")
                    if xml_PerformanceId:
                        PerformanceId = xml_PerformanceId[0].text
                        pid_dict[ISIN] = PerformanceId
                        # print(pid_dict)
                        PerformanceId_list.append(pid_dict)

        print(PerformanceId_list)
        return PerformanceId_list


    def xml_market(self):
        xml_list = []
        PerformanceId_list = []
        id_list = self.get_white()
        pid = self.get_PerformanceId()
        for m in id_list:
            m = m.split('==')
            ISIN = m[0]
            MS_SECID = m[1]

            x = []
            for i in pid:
                for k, v in i.items():
                    if k == ISIN:
                        id = v
                        nav_list = []
                        fqnav_list = []
                        nav_data_list = []

                        curr_time = datetime.now()
                        EndDate = curr_time.strftime("%Y-%m-%d")

                        url2 = f"https://edw.morningstar.com/HistoryData/HistoryData.aspx?ClientId=magnumhk&DataType=Price&PerformanceId={id}&StartDate=2021-12-20&EndDate={EndDate}&Obsolete=1"
                        url3 = f"https://edw.morningstar.com/HistoryData/HistoryData.aspx?ClientId=magnumhk&DataType=Rips&PerformanceId={id}&StartDate=2021-12-20&EndDate={EndDate}&Obsolete=1&from=from_parent_mindnote"

                        res2 = requests.get(url=url2, headers=self.headers)
                        res3 = requests.get(url=url3, headers=self.headers)

                        nav_detail = res2.text
                        fqnav_detail = res3.text

                        nav_data = nav_detail.split("\r\n")[1]
                        y = nav_data.split(";")
                        nav_Date = y[2]
                        CurrencyISO = y[3]
                        PreTaxNav = str(Decimal(y[4]).quantize(Decimal('0.000000'), rounding='ROUND_HALF_UP')).rstrip("0")

                        nav_data_list.append(nav_Date)
                        nav_data_list.append(CurrencyISO)
                        nav_data_list.append(PreTaxNav)

                        fqnav_data = fqnav_detail.split("\r\n")[1]
                        yy = fqnav_data.split(";")
                        fqnav_Date = yy[2]
                        # Unit_BAS = yy[4]
                        Unit_BAS = str(Decimal(yy[4]).quantize(Decimal('0.000000'), rounding='ROUND_HALF_UP')).rstrip("0")

                        nav_data_list.append(Unit_BAS)
                        nav_data_list.append(ISIN)
                        nav_data_list.sort()
                        # print(nav_data_list)
            xml_list.append(nav_data_list)
            xml_list.sort()
        print(xml_list)
        return(xml_list)


    def read_market_csv(self):
        market_csv_dic = {}
        with open(self.market_filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            i = 0
            for row in reader:
                if i == 0:
                    pass
                else:
                    row = row[0:4] + row[-1:]
                    reportDate = row[-1]  # 读取csv中的日期
                    if "/" in reportDate:
                        csv_reportDate = reportDate.split("/")  # csv中，年月日，根据"/"切割
                        reportDate = self.date_conversion(csv_reportDate)  # 把切割后的列表传进日期转换的方法date_conversion()
                    if "-" in reportDate:  # 同理，月份1~9加0，日期1~9加0
                        csv_reportDate = reportDate.split("-")
                        reportDate = self.date_conversion(csv_reportDate)
                    row[-1] = reportDate

                    row.sort()
                    market_csv_dic[f"第{i}行"] = row
                i += 1
            print(market_csv_dic)
            return market_csv_dic


    def compare_market(self):
        '''
        比较 market.csv文件
        '''
        times = self.get_time()
        print('\n>>>>>>>>>>正在比较market.csv文件>>>>>>>>>>')
        market_list = self.xml_market()
        # print(market_list)
        print(f"ms数据量：",len(market_list))
        csv_data = self.read_market_csv()
        # print(csv_data)
        print(f"market.csv数据量：",len(csv_data))

        if len(market_list) == len(csv_data):
            j = 0
            for k, v in csv_data.items():
                i = 0
                for cm in market_list:
                    if operator.eq(cm, v):
                        i += 1
                        j += 1
                    else:
                        pass
                # i += 1 # 打印相同数据
                if i != 1:# 数据相同，i计数+1,即相同的数据不写入txt
                    self.write_compare_data('result_market.txt', k, times)
                    print(f'数据不一致：',k)
            if j == len(market_list):# 数据比对相同时，j的计数+1，相同数=总数，数据一致。
                print('\nmarket.csv >>>校验通过，数据一致!')
        else:
            print('数据量不一致')
            self.write_compare_data('result_manager.txt', '数据量不一致', times)


if __name__ == '__main__':
    c = Comparexml()

    # 获取PerformanceId
    # c.get_PerformanceId()

    # 获取xml_market数据
    # c.xml_market()

    # 读取market.csv内容
    # c.read_market_csv()

    # 校验market.csv内容
    c.compare_market()


    endtime = datetime.now()
    print("\nRunTime: {}h-{}m-{}s".format(endtime.hour-starttime.hour, endtime.minute-starttime.minute, endtime.second-starttime.second))