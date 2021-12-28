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
        self.distribution_filepath = r'D:\ms\distribution_1640479203977.csv'
        self.white_filepath = r'D:\ms\white_v6.xlsx'


    def get_white(self):
        '''
        获取白名单 ISIN==MS_SECID
        '''
        id = []
        with open('white_all_162.txt', 'r', encoding='utf-8')as f:
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


    def get_weight_num(self,weight_list_detail, weight_list):
        """
        获取weight从大到小的坐标
        :return:
        """
        new_weight_num = []
        for wd in weight_list_detail:
            for xx in weight_list:
                for k, v in xx.items():
                    if wd == v:
                        new_weight_num.append(k)
        return new_weight_num


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
        return xlsx_list


    def xml_distribution(self):
        xml_list = []
        id_list = self.get_white()
        for m in id_list:
            m = m.split('==')
            ISIN = m[0]
            MS_SECID = m[1]

            url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"

            res = requests.get(url)

            if res.status_code == 200:
                print(f">>>>>>>>>>开始获取'{MS_SECID}'的数据>>>>>>>>>>")
                xml_distribution = res.text

                if xml_distribution:
                    data = requests.get(url=url, headers=self.headers)
                    selector = etree.XML(data.content)
                    xml_list_detail = []

                    ID = f'{ISIN}'
                    distType = ["100", "200", "300"]  # 100-地区分布  200-行业分布  300-资产类型分布
                    for d in distType:

                        if d == "100":
                            """
                            地区分布
                            1 United States---美国
                            2 Canada---加拿大
                            3 Latin America---拉丁美洲
                            4 United Kingdom---英国
                            5 Eurozone---欧元区
                            6 Europe - ex Euro---欧洲-欧元以外
                            7 Europe - Emerging---欧洲-新兴市场
                            8 Africa---非洲
                            9 Middle East---中东地区
                            10 Japan---日本
                            11 Australasia---大洋洲
                            12 Asia - Developed---亚洲--发达国家
                            13 Asia - Emerging---亚洲
                            14 Emerging Market---新兴市场
                            15 Developed Country---发达国家
                            16 Not Classified---未分类
                            """
                            dict3 = self.read_xlsx()[0]
                            if ID in dict3:
                                for k, v in dict3.items():
                                    if k == ID:
                                        if v == "1" or v == "4":  # 股票型 or 混合型
                                            for i in range(1,17):
                                                distKey = selector.xpath(
                                                    f"/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioBreakdown[@_SalePosition='L']/RegionalExposure/BreakdownValue[@Type={i}]")
                                                reportDate = selector.xpath(
                                                    f"/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioSummary/Date")
                                                if distKey:
                                                    key1 = distKey[0].text
                                                    x = []
                                                    if key1 != "0":
                                                        print(f"distType={d}---@Type={i}---distKey:", distKey[0].text)
                                                        x.append(f"{d}")
                                                        x.append(f'{i}')
                                                        x.append(str(Decimal(str(float(key1))).quantize(Decimal('0.0000'), rounding='ROUND_HALF_UP') / 100).rstrip("0"))
                                                        x.append(ISIN)
                                                        x.append(reportDate[0].text)
                                                        x.sort()
                                                        xml_list_detail.append(x)
                                                    else:
                                                        print(f"distType={d}---@Type={i}---distKey: 0")

                                        if v == "2" or v == "3":  # 债券型 or 货币型
                                            for i in range(1, 17):
                                                distKey = selector.xpath(
                                                    f"/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioBreakdown[@_SalePosition='L']/BondRegionalExposure/BreakdownValue[@Type={i}]")
                                                reportDate = selector.xpath(
                                                    f"/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioSummary/Date")
                                                if distKey:
                                                    key1 = distKey[0].text
                                                    x = []
                                                    if key1 != "0":
                                                        print(f"distType={d}---@Type={i}---distKey:", distKey[0].text)
                                                        x.append(f"{d}")
                                                        x.append(f'{i}')
                                                        x.append(str(Decimal(str(float(key1))).quantize(Decimal('0.0000'), rounding='ROUND_HALF_UP') / 100).rstrip("0"))
                                                        x.append(ISIN)
                                                        x.append(reportDate[0].text)
                                                        x.sort()
                                                        xml_list_detail.append(x)
                                                    else:
                                                        print(f"distType={d}---@Type={i}---distKey: 0")

                                        if v == "8":  # 另类投资型
                                            pass

                        if d == "200":
                            """
                                101 Basic Materials---基础材料
                                102 Consumer Cyclical---周期性消费品
                                103 Financial Services---金融服务
                                104 Real Estate---房地产
                                205 Consumer Defensive---必需品类消费品
                                206 Healthcare---医疗保健
                                207 Utilities---公用事业
                                308 Communication Services---通信服务
                                309 Energy---能源
                                310 Industrials---工业类
                                311 Technology---技行业
                            """
                            dict3 = self.read_xlsx()[0]
                            if ID in dict3:
                                for k, v in dict3.items():
                                    if k == ID:
                                        if v == "1" or v == "4":  # 股票型 or 混合型
                                            industry_list = [101, 102, 103, 104, 205, 206, 207, 308, 309, 310, 311]
                                            for i in industry_list:
                                                distKey = selector.xpath(
                                                    f"/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioBreakdown[@_SalePosition='L']/GlobalStockSectorBreakdown/BreakdownValue[@Type={i}]")
                                                reportDate = selector.xpath(
                                                    f"/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioSummary/Date")
                                                if distKey:
                                                    key1 = distKey[0].text
                                                    x = []
                                                    if key1 != "0":
                                                        print(f"distType={d}---@Type={i}---distKey:", distKey[0].text)
                                                        x.append(f"{d}")
                                                        x.append(f'{i}')
                                                        x.append(str(Decimal(str(float(key1))).quantize(Decimal('0.0000'), rounding='ROUND_HALF_UP') / 100).rstrip("0"))
                                                        x.append(ISIN)
                                                        x.append(reportDate[0].text)
                                                        x.sort()
                                                        xml_list_detail.append(x)
                                                    else:
                                                        print(f"distType={d}---@Type={i}---distKey: 0")

                                        if v == "2":  # 债券型
                                            pass

                                        if v == "3":  # 货币型
                                            pass

                                        if v == "8":  # 另类投资型
                                            pass

                        if d == "300":
                            dict3 = self.read_xlsx()[0]
                            if ID in dict3:
                                for k, v in dict3.items():
                                    if k == ID:
                                        if v == "2" or v == "3":  # 债券型 or 货币型
                                            """                      
                                                10 Government---政府债券
                                                20 Municipal---市政债券
                                                30 Corporate---企业债券
                                                40 Securitized---证券化资产
                                                50 Cash & Equivalents---现金及现金等价物
                                                60 Derivative---衍生品
                                            """
                                            for i in range(10, 70, 10):
                                                distKey_L = selector.xpath(
                                                    f'/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioBreakdown[@_SalePosition="L"]/GlobalBondSector/GlobalBondSectorBreakdown[@Level="1"]/BreakdownValue[@Type={i}]')
                                                distKey_S = selector.xpath(
                                                    f'/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioBreakdown[@_SalePosition="S"]/GlobalBondSector/GlobalBondSectorBreakdown[@Level="1"]/BreakdownValue[@Type={i}]')
                                                reportDate = selector.xpath(
                                                    f"/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioSummary/Date")

                                                if distKey_L:
                                                    if distKey_S:
                                                        key_L = distKey_L[0].text
                                                        key_S = distKey_S[0].text
                                                        key = float(key_L) - float(key_S)
                                                        x = []
                                                        if key_L:
                                                            if key != 0:
                                                                print(f"distType={d}---@Type={i}---distKey:", key)
                                                                x.append(f"{d}")
                                                                x.append(f'{i}')
                                                                x.append(str(Decimal(str(float(key))).quantize(Decimal('0.0000'),rounding='ROUND_HALF_UP') / 100).rstrip("0"))
                                                                x.append(ISIN)
                                                                x.append(reportDate[0].text)
                                                                x.sort()
                                                                xml_list_detail.append(x)
                                                    else:
                                                        key_L = distKey_L[0].text
                                                        key = float(key_L)
                                                        x = []
                                                        if key_L:
                                                            if key != 0:
                                                                print(f"distType={d}---@Type={i}---distKey:", key)
                                                                x.append(f"{d}")
                                                                x.append(f'{i}')
                                                                x.append(str(Decimal(str(float(key))).quantize(Decimal('0.0000'),rounding='ROUND_HALF_UP') / 100).rstrip("0"))
                                                                x.append(ISIN)
                                                                x.append(reportDate[0].text)
                                                                x.sort()
                                                                xml_list_detail.append(x)
                                                else:
                                                    pass

                                        else:
                                            """                      
                                             1 Stock---股票
                                             3 Bond---债券
                                             5 Preferred---优先股
                                             6 Convertible---可转债
                                             7 Cash---现金
                                             8 Other---其他
                                            """
                                            AssetType_list = [1, 3, 5, 6, 7, 8]
                                            for i in AssetType_list:
                                                distKey_L = selector.xpath(
                                                    f'/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioBreakdown [@_SalePosition="L"]/AssetAllocation/BreakdownValue[@Type={i}]')
                                                distKey_S = selector.xpath(
                                                    f'/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioBreakdown [@_SalePosition="S"]/AssetAllocation/BreakdownValue[@Type={i}]')
                                                reportDate = selector.xpath(
                                                    f"/FundShareClass/Fund/PortfolioList/Portfolio/PortfolioSummary/Date")

                                                if distKey_L:
                                                    if distKey_S:
                                                        key_L = distKey_L[0].text
                                                        key_S = distKey_S[0].text
                                                        key = float(key_L) - float(key_S)
                                                        x = []
                                                        if key_L:
                                                            if key != 0:
                                                                print(f"distType={d}---@Type={i}---distKey:", key)
                                                                x.append(f"{d}")
                                                                x.append(f'{i}')
                                                                x.append(str(Decimal(str(float(key))).quantize(Decimal('0.0000'),rounding='ROUND_HALF_UP') / 100).rstrip("0"))
                                                                x.append(ISIN)
                                                                x.append(reportDate[0].text)
                                                                x.sort()
                                                                xml_list_detail.append(x)
                                                    else:
                                                        key_L = distKey_L[0].text
                                                        key = float(key_L)
                                                        x = []
                                                        if key_L:
                                                            if key != 0:
                                                                print(f"distType={d}---@Type={i}---distKey:", key)
                                                                x.append(f"{d}")
                                                                x.append(f'{i}')
                                                                x.append(str(Decimal(str(float(key))).quantize(Decimal('0.0000'),rounding='ROUND_HALF_UP') / 100).rstrip("0"))
                                                                x.append(ISIN)
                                                                x.append(reportDate[0].text)
                                                                x.sort()
                                                                xml_list_detail.append(x)
                                                else:
                                                    pass

                    if xml_list_detail:
                        for x in xml_list_detail:
                            xml_list.append(x)
                            xml_list.sort()
            print(xml_list)
        return xml_list


    def read_distribution_csv(self):
        distribution_csv_dic = {}
        with open(self.distribution_filepath, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            i = 0
            for row in reader:
                if i == 0:
                    pass
                else:
                    row = row[0:5]
                    reportDate = row[-1]  # 读取csv中的日期
                    if "/" in reportDate:
                        csv_reportDate = reportDate.split("/")  # csv中，年月日，根据"/"切割
                        reportDate = self.date_conversion(csv_reportDate)  # 把切割后的列表传进日期转换的方法date_conversion()
                    if "-" in reportDate: # 同理，月份1~9加0，日期1~9加0
                        csv_reportDate = reportDate.split("-")
                        reportDate = self.date_conversion(csv_reportDate)
                    row[-1] = reportDate

                    row.sort()
                    distribution_csv_dic[f"第{i}行"] = row
                i += 1
            print(distribution_csv_dic)
            return distribution_csv_dic


    def compare_distribution(self):
        '''
        比较 distribution.csv文件
        '''
        times = self.get_time()
        print('\n>>>>>>>>>>正在比较distribution.csv文件>>>>>>>>>>')
        distribution_list = self.xml_distribution()
        # print(distribution_list)
        print(f"ms数据量：",len(distribution_list))
        csv_data = self.read_distribution_csv()
        # print(csv_data)
        print(f"distribution.csv数据量：",len(csv_data))

        if len(distribution_list) == len(csv_data):
            j = 0
            for k, v in csv_data.items():
                i = 0
                for cm in distribution_list:
                    if operator.eq(cm, v):
                        i += 1
                        j += 1
                    else:
                        pass
                # i += 1 # 打印相同数据
                if i != 1:# 数据相同，i计数+1,即相同的数据不写入txt
                    self.write_compare_data('result_distribution.txt', k, times)
                    print(f'数据不一致：',k)
            if j == len(distribution_list):# 数据比对相同时，j的计数+1，相同数=总数，数据一致。
                print('\ndistribution.csv >>>校验通过，数据一致!')
        else:
            print('数据量不一致')
            self.write_compare_data('result_distribution.txt', '数据量不一致', times)

if __name__ == '__main__':
    c = Comparexml()

    # 获取xml_distribution数据
    # c.xml_distribution()

    # 读取distribution.csv内容
    # c.read_distribution_csv()

    # 校验distribution.csv内容
    c.compare_distribution()


    endtime = datetime.now()
    print("\nRunTime: {}h-{}m-{}s".format(endtime.hour-starttime.hour, endtime.minute-starttime.minute, endtime.second-starttime.second))