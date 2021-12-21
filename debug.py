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
import datetime
import xlrd


class Comparexml:
    def __init__(self):
        # self.url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"
        self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36'}
        self.managercsv_filepath = r'D:\ms\manager_debug.csv'
        self.holdingcsv_filepath = r'D:\ms\holding_debug.csv'
        self.basciInfo_filepath = r'D:\ms\basicInfo_debug.csv'
        self.white_filepath = r'D:\ms\white_v3.xlsx'


    def get_white(self):
        '''
        获取白名单 ISIN==MS_SECID
        '''
        id = []
        with open('white_debug.txt', 'r', encoding='utf-8')as f:
            for x in f.readlines():
                id.append(x.replace('\n', ''))
        return id

    # def get_MS_SECID(self):
    #     id_list = self.get_white()
    #     MS_SECID_LIST = []
    #     # print(id_list)
    #     for m in id_list:
    #         # isin==ms_secid
    #         # print(f'{m}')
    #         m = m.split('==')
    #         ISIN = m[0]
    #         MS_SECID = m[1]
    #         MS_SECID_LIST.append(MS_SECID)
    #     return MS_SECID_LIST

    def get_time(self):
        times = time.strftime("%Y%m%d%H%MS", time.localtime())
        return times
    #
    #         url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"
    #         # url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id=F0GBR06111&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"
    #
    #         data = requests.get(url=url,headers=self.headers)
    #         print(len(data.text))
    #
    #         selector = etree.XML(data.content)
    #
    #         GivenName = selector.xpath('//ProfessionalInformation[@_Id = "124181"]//GivenName')
    #         FamilyName = selector.xpath('//ProfessionalInformation[@_Id = "124181"]//FamilyName')
    #         # 基金经理名称
    #         managerName = GivenName + FamilyName
    #         # 基金经理任期(管理起始日期)
    #         managerStartDate = selector.xpath('//ProfessionalInformation[@_Id="124181"]/../StartDate')
    #         # 基金经理任期(管理结束日期)
    #         managerEndtDate = selector.xpath('//ProfessionalInformation[@_Id="124181"]/../EndDate')
    #         # print(managerName)
    #         print(managerName[0].text,managerName[1].text)
    #         print(managerStartDate[0].text)
    #         print(managerEndtDate[0].text)

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


    def xml_manager(self):
        # MS_SECID_list = self.get_MS_SECID()
        xml_list = []
        id_list = self.get_white()
        for m in id_list:
            # isin==ms_secid
            # print(f'{m}')
            m = m.split('==')
            ISIN = m[0]
            MS_SECID = m[1]


            url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"
            # url = "https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id=F0GBR06111&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"
            res = requests.get(url)

            if res.status_code == 200:
                print(f">>>>>>>>>>开始获取{MS_SECID}的数据>>>>>>>>>>")
                xml_managers = res.text
                xml_manager = re.findall('<ManagerList>(.*?)</ManagerList>', xml_managers,
                                         re.S)  # 修饰符re.S  使.匹配包括换行在内的所有字符
                # 优先取中文名，无中文名取英文名
                # xml_MultilingualVariation = re.findall('<MultilingualVariation _Id="(.*?)"><LanguageVariation _LanguageId="0L00000082">(.*?)</PersonalInformation>',xml_managers, re.S)
                # dm = dict(xml_MultilingualVariation)
                if xml_manager:
                    manager_list = xml_manager[0]
                    manager_detail = manager_list.split("</ManagerDetail>")
                    # print(len(manager_detail))
                    for m in manager_detail:
                        xml_list_detail = []
                        # 基金经理任期(管理结束日期)
                        managerEndDate = re.findall("<EndDate>(.*?)</EndDate>.*", m)
                        # csv文件取没有managerEndDate的数据
                        if not managerEndDate:
                            manager_id = re.findall('<ProfessionalInformation _Id="(.*?)" _Status', m)
                            if manager_id:
                                print(f"manager_id:", manager_id[0])
                                xml_list_detail.append(manager_id[0])

                                # xml_MultilingualVariation = re.findall(f'<MultilingualVariation _Id="{manager_id[0]}">(.*?)</MultilingualVariation>', m)
                                # managerStartDate = selector.xpath('//ProfessionalInformation[@_Id="124181"]/../StartDate')
                                data = requests.get(url=url, headers=self.headers)
                                selector = etree.XML(data.content)
                                xml_MultilingualVariation = selector.xpath(f'//MultilingualVariation[@_Id="{manager_id[0]}"]/../MultilingualVariation')
                                if xml_MultilingualVariation:
                                    # xx = xml_MultilingualVariation[0].text
                                    # print(xx)
                                    # MultilingualVariation = xml_MultilingualVariation[0]
                                    # xml_LanguageVariation = re.findall('<LanguageVariation _LanguageId="0L00000082">(.*?)</PersonalInformation>', MultilingualVariation)
                                    xml_LanguageVariation = selector.xpath('//LanguageVariation[@_LanguageId="0L00000082"]/../LanguageVariation')
                                    if xml_LanguageVariation:
                                        # LanguageVariation_detail = xml_LanguageVariation[0]
                                        # print(LanguageVariation_detail)
                                        # GivenName_cn = re.findall("<GivenName>(.*?)</GivenName>", LanguageVariation_detail, re.S)
                                        GivenName_cn = selector.xpath(f'//MultilingualVariation[@_Id="{manager_id[0]}"]/LanguageVariation [@_LanguageId="0L00000082"]//GivenName')
                                        # FamilyName_cn = re.findall("<FamilyName>(.*?)</FamilyName>", LanguageVariation_detail, re.S)
                                        FamilyName_cn = selector.xpath(f'//MultilingualVariation[@_Id="{manager_id[0]}"]/LanguageVariation [@_LanguageId="0L00000082"]//FamilyName')
                                        # manager_name = FamilyName_cn[0] + GivenName_cn[0]
                                        manager_name = FamilyName_cn + GivenName_cn
                                        if manager_name:

                                            # print(f"GivenName:", GivenName_cn[0])
                                            # print(f"FamilyName:", FamilyName_cn[0])
                                            print(f"GivenName:", GivenName_cn[0].text)
                                            print(f"FamilyName:", FamilyName_cn[0].text)
                                            manager_name = FamilyName_cn[0].text + GivenName_cn[0].text
                                            xml_list_detail.append(manager_name)
                                        else:
                                            GivenName_en = re.findall("<GivenName>(.*?)</GivenName>", m)
                                            FamilyName_en = re.findall("<FamilyName>(.*?)</FamilyName>", m)
                                            print(f"GivenName:", GivenName_en[0])
                                            print(f"FamilyName:", FamilyName_en[0])
                                            manager_name = GivenName_en[0] + ' ' + FamilyName_en[0]
                                            xml_list_detail.append(manager_name)
                                    else:
                                        GivenName_en = re.findall("<GivenName>(.*?)</GivenName>", m)
                                        FamilyName_en = re.findall("<FamilyName>(.*?)</FamilyName>", m)
                                        print(f"GivenName:", GivenName_en[0])
                                        print(f"FamilyName:", FamilyName_en[0])
                                        manager_name = GivenName_en[0] + ' ' + FamilyName_en[0]
                                        xml_list_detail.append(manager_name)
                                else:
                                    GivenName_en = re.findall("<GivenName>(.*?)</GivenName>", m)
                                    FamilyName_en = re.findall("<FamilyName>(.*?)</FamilyName>", m)
                                    print(f"GivenName:", GivenName_en[0])
                                    print(f"FamilyName:", FamilyName_en[0])
                                    manager_name = GivenName_en[0] + ' ' + FamilyName_en[0]
                                    xml_list_detail.append(manager_name)



                                # if dm:
                                #     for k, v in dm.items():
                                #         if k == manager_id[0]:
                                #             GivenName_cn = re.findall("<GivenName>(.*?)</GivenName>", v)
                                #             FamilyName_cn = re.findall("<FamilyName>(.*?)</FamilyName>", v)
                                #             manager_name = FamilyName_cn[0] + GivenName_cn[0]
                                #             print(f"GivenName:", GivenName_cn[0])
                                #             print(f"FamilyName:", FamilyName_cn[0])
                                #             xml_list_detail.append(manager_name)
                                #         else:
                                #             GivenName_en = re.findall("<GivenName>(.*?)</GivenName>", m)
                                #             FamilyName_en = re.findall("<FamilyName>(.*?)</FamilyName>", m)
                                #             print(f"GivenName:", GivenName_en[0])
                                #             print(f"FamilyName:", FamilyName_en[0])
                                #             manager_name = GivenName_en[0] + ' ' + FamilyName_en[0]
                                #             xml_list_detail.append(manager_name)
                                # else:
                                #     GivenName_en = re.findall("<GivenName>(.*?)</GivenName>", m)
                                #     FamilyName_en = re.findall("<FamilyName>(.*?)</FamilyName>", m)
                                #     print(f"GivenName:", GivenName_en[0])
                                #     print(f"FamilyName:", FamilyName_en[0])
                                #     manager_name = GivenName_en[0] + ' ' + FamilyName_en[0]
                                #     xml_list_detail.append(manager_name)
                            # 基金经理任期(管理起始日期)
                            managerStartDate = re.findall("<StartDate>(.*?)</StartDate>", m)
                            if managerStartDate:
                                print(f"managerStartDate:", managerStartDate[0])
                                # xml_list_detail.append(managerStartDate[0].replace('-','/').replace('/0','/'))
                                xml_list_detail.append(managerStartDate[0])

                            else:
                                print("缺少managerStartDate")
                                # assert False
                            print("=============================")

                        else:
                            pass
                        if xml_list_detail:
                            xml_list_detail.append(ISIN)
                            xml_list_detail.sort()
                            xml_list.append(xml_list_detail)

            print(xml_list)
        return xml_list


    def read_manager_csv(self,managercsv_filepath):
        manager_csv_dic = {}
        with open(managercsv_filepath, 'r') as f:
            reader = csv.reader(f)
            i = 0
            for row in reader:
                if i == 0:
                    pass
                else:
                    row = row[0:4]
                    start_date = row[3]  # 读取csv中的日期
                    if "/" in start_date:
                        csv_managerStartDate = start_date.split("/")  # csv中，年月日，根据"/"切割
                        start_date = self.date_conversion(csv_managerStartDate)  # 把切割后的列表传进日期转换的方法date_conversion()
                    if "-" in start_date: # 同理，月份1~9加0，日期1~9加0
                        csv_managerStartDate = start_date.split("-")
                        start_date = self.date_conversion(csv_managerStartDate)
                    row[3] = start_date
                    row.sort()
                    manager_csv_dic[f"第{i}行"] = row
                i += 1
            # print(manager_csv_dic)
            return manager_csv_dic

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


    def compare_manager(self):
        '''
        比较 manager.csv文件
        '''
        times = self.get_time()
        print('\n>>>>>>>>>>正在比较manager.csv文件>>>>>>>>>>')
        manager_list = self.xml_manager()
        # print(manager_list)
        print(f"ms数据量：",len(manager_list))
        csv_data = self.read_manager_csv(self.managercsv_filepath)
        print(csv_data)
        print(f"manager.csv数据量：",len(csv_data))

        if len(manager_list) == len(csv_data):
            j = 0
            for k, v in csv_data.items():
                i = 0
                for cm in manager_list:
                    if operator.eq(cm, v):
                        i += 1
                        j += 1
                    else:
                        pass
                # i += 1 # 打印相同数据
                if i != 1:# 数据相同，i计数+1,即相同的数据不写入txt
                    self.write_compare_data('result_manager.txt', k, times)
                    print(f'数据不一致：',k)
            if j == len(manager_list):# 数据比对相同时，j的计数+1，相同数=总数，数据一致。
                print('\nmanager.csv >>>校验通过，数据一致!')
        else:
            print('数据量不一致')
            self.write_compare_data('result_manager.txt', '数据量不一致', times)


    def xml_holding(self):
        # MS_SECID_list = self.get_MS_SECID()
        new_xml_list = []
        id_list = self.get_white()
        for m in id_list:
            xml_list = []
            # isin==ms_secid
            # print(f'{m}')
            m = m.split('==')
            ISIN = m[0]
            MS_SECID = m[1]

            url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"
            res = requests.get(url)

            if res.status_code == 200:
                print(f">>>>>>>>>>开始获取{MS_SECID}的数据>>>>>>>>>>")
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

                    weight_list_detail = [] # [6.99291]
                    weight_list = [] # [{0: 6.99291}]
                    # 遍历序列中的元素及其下标
                    for num, hd in enumerate(holding_detail):
                        xml_list_detail = [] # ['HK0000012440', 'IE0008370151', 'First Sentier Asia Strat Bd I USDInc', '6.99291', '2021-06-30']
                        xml_dic_detail = {} # {0: ['HK0000012440', 'IE0008370151', 'First Sentier Asia Strat Bd I USDInc', '6.99291', '2021-06-30']}
                        weight_dic = {}
                        Weighting = re.findall("<Weighting>(.*?)</Weighting>", hd)
                        if Weighting:
                            print(f"Weighting", Weighting[0])
                            weight_text = Weighting[0]
                            weight_float = float(Weighting[0])
                            # 持仓占比
                            xml_list_detail.append(ISIN)
                            isin_code = re.findall("<ISIN>(.*?)</ISIN>", hd)
                            if isin_code:
                                print(isin_code[0])
                                xml_list_detail.append(isin_code[0])
                            currency = re.findall('<Currency _Id="(.*?)">',hd)
                            if currency:
                                print(currency[0])
                                xml_list_detail.append(currency[0])
                            security_name = re.findall("<SecurityName>(.*?)</SecurityName>", hd)
                            if security_name:
                                print(security_name[0])
                                xml_list_detail.append(security_name[0])

                            xml_list_detail.append(weight_text)
                            xml_list_detail.append(holding_detail_date[0])
                            xml_list_detail.sort()

                            xml_dic_detail[num] = xml_list_detail # {0: ['HK0000012440', 'IE0008370151', 'First Sentier Asia Strat Bd I USDInc', '6.99291', '2021-06-30']}
                            weight_dic[num] = weight_float # {0: 6.99291}

                            weight_list.append(weight_dic)
                            weight_list_detail.append(weight_float)
                            print("================================")
                            xml_list.append(xml_dic_detail)

                    weight_list_detail = sorted(weight_list_detail, key=float, reverse=True)
                    # print(weight_list_detail)
                    weight_num_list = self.get_weight_num(weight_list_detail, weight_list)
                    print(f"排序后的weight坐标: {weight_num_list}")
                    # 根据新坐标获取列表
                    for wl in weight_num_list[:10]:
                        for xxx in xml_list:
                            for k, v in xxx.items():
                                if wl == k:
                                    new_xml_list.append(v)
                print(new_xml_list)
        return new_xml_list

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




    def read_holding_csv(self):
        holding_csv_dic = {}
        with open(self.holdingcsv_filepath, 'r', encoding='utf-8') as f:
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


    def read_xlsx(self):
        workbook = xlrd.open_workbook(self.white_filepath)
        Data_sheet = workbook.sheets()[0]  # 通过索引获取
        rowNum = Data_sheet.nrows  # sheet行数
        colNum = Data_sheet.ncols  # sheet列数
        white_dic = {}
        # 基金类型  1-股票型  2-债券型  3-货币型  4-混合型  8-另类投资型
        fundInvestType_list = []
        # 基金地域  0-无地区偏好  10-亚太市场  11-中国市场  21-美国市场  30-欧洲市场  70-新兴市场  90-全球市场
        fundRegion_list = []
        # 0-无行业偏好  1-科技  2-消费  3-医疗  4-金融  5-工业  6-房地产  7-公用事业  8-能源  9-通信  10-基础材料
        # 债券型和货币型没有该字段
        fundIndustry_list = []
        for i in range(1, rowNum):
            white_list = []
            for j in range(colNum):
                white_list.append(Data_sheet.cell_value(i, j))
            white_dic[white_list[-3]] = white_list[-2:]
        print(f'中信白名单_基金分类情况_v3: \n{white_dic}')


        return white_dic


    def xml_basicInfo(self):
        # MS_SECID_list = self.get_MS_SECID()
        xml_list = []
        id_list = self.get_white()
        for m in id_list:
            # isin==ms_secid
            # print(f'{m}')
            m = m.split('==')
            ISIN = m[0]
            MS_SECID = m[1]

            url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"
            res = requests.get(url)

            if res.status_code == 200:
                print(f">>>>>>>>>>开始获取{MS_SECID}的数据>>>>>>>>>>")
                xml_basicInfo = res.text
                xml_basicInfo_FundShareClass = re.findall('<FundShareClass .*?>(.*?)</FundShareClass>', xml_basicInfo,re.S)  # 修饰符re.S  使.匹配包括换行在内的所有字符
                # fundNameEN
                xml_basicInfo_Operation = re.findall('<Operation>(.*?)</Operation>', xml_basicInfo,re.S)
                # fundNameSC
                xml_basicInfo_MultilingualVariation = re.findall(f'<MultilingualVariation _Id="{MS_SECID}">(.*?)</MultilingualVariation>', xml_basicInfo, re.S)
                # baseCurrency,基金信息板块下展示该币种
                xml_basicInfo_PerformanceId = re.findall('<PerformanceId>(.*?)</PerformanceId>', xml_basicInfo, re.S)
                # 基金市场状态  0-停止  1-开放期  2-募集期
                xml_basicInfo_Status = re.findall(f'<FundShareClass _Id="{MS_SECID}" _FundId=".*?" _Status="(.*?)">',xml_basicInfo,re.S)

                # fundIndustry,基金所属行业




                if xml_basicInfo:
                    basicInfo_list = xml_basicInfo_FundShareClass[0]
                    basicInfo_list_Operation = xml_basicInfo_Operation[0]
                    basicInfo_list_MultilingualVariation = xml_basicInfo_MultilingualVariation[0]
                    # # 币种位置固定可用
                    # basicInfo_list_PerformanceId = xml_basicInfo_PerformanceId[-1]
                    basicInfo_list_PerformanceId = [c for c in xml_basicInfo_PerformanceId if "CurrencyId" in c]


                    basicInfo_FundShareClass = basicInfo_list.split("</FundShareClass>")
                    basicInfo_ShareClassBasics =basicInfo_list_Operation.split("</LegalName>")
                    basicInfo_MultilingualVariation = basicInfo_list_MultilingualVariation.split('<LanguageVariation _LanguageId="0L00000082">')
                    # basicInfo_PerformanceId = basicInfo_list_PerformanceId.split("</CurrencyId>")
                    basicInfo_PerformanceId = basicInfo_list_PerformanceId[0]
                    # shareClassCurrency,除基金信息板块外其他页面展示这个币种
                    basicInfo_shareClassCurrency = basicInfo_list_Operation.split("</Currency>")


                    for m in basicInfo_FundShareClass:
                        xml_list_detail = []
                        # 父基金编码
                        parentCode = re.findall('<Fund _Id="(.*?)"',m)
                        if parentCode:
                            print(f"parentCode:",parentCode[0])
                            xml_list_detail.append(parentCode[0])
                        for name in basicInfo_ShareClassBasics:
                            fundNameEN = re.findall("<LegalName>(.*)",name)
                            if fundNameEN:
                                print(f"fundNameEN:", fundNameEN[0])
                                xml_list_detail.append(fundNameEN[0])
                        for nameSC in basicInfo_MultilingualVariation:
                            fundNameSC = re.findall("<Name>(.*?)</Name>",nameSC)
                            if fundNameSC:
                                print(f"fundNameSC:", fundNameSC[0])
                                xml_list_detail.append(fundNameSC[0])
                        # for Currency in basicInfo_PerformanceId:
                        baseCurrency = re.findall("<CurrencyId>(.*)</CurrencyId>",basicInfo_PerformanceId)
                        if baseCurrency:
                            print(f"baseCurrency:", baseCurrency[0])
                            xml_list_detail.append(baseCurrency[0])
                        for Currency in basicInfo_shareClassCurrency:
                            shareClassCurrency = re.findall('<Currency _Id="(.*?)">',Currency)
                            if shareClassCurrency:
                                print(f"shareClassCurrency:", shareClassCurrency[0])
                                xml_list_detail.append(shareClassCurrency[0])

                        if basicInfo_Status:
                           basicInfo_Status = xml_basicInfo_Status[0]
                           print(f"shareClassCurrency:", basicInfo_Status[0])

            #                 for d in basicInfo_detail_date:
            #                     # 报告日期
            #                     reportDate = re.findall("<Date>(.*?)</Date>",d)
            #                     print(f"reportDate",reportDate[0])
            #                     xml_list_detail.append(reportDate[0])
            #                 print("=============================")
            #
            #             if xml_list_detail:
            #                 xml_list_detail.append(ISIN)
            #                 # xml_list_detail.sort()
            #                 xml_list.append(xml_list_detail)
            #
            # print(xml_list)
        return xml_list







if __name__ == '__main__':
    c = Comparexml()

    # c.xml_manager()
    # managercsv_filepath =c.managercsv_filepath
    # c.read_manager_csv(managercsv_filepath=managercsv_filepath)


    # # 校验manager.csv
    # c.compare_manager()

    # #获取xml数据
    # c.xml_holding()
    # # aa = c.xml_holding()
    # # print("打印根据weight排名前十个：")
    # # for a in aa:
    # #     print(a)

    # # 读取holding.csv内容
    # c.read_holding_csv()

    # # 校验holding.csv
    # c.compare_holding()
    #
    # c.xml_basicInfo()
    c.read_xlsx()