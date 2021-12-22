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

starttime = datetime.now()

class Comparexml:
    def __init__(self):
        # self.url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"
        self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36'}
        self.managercsv_filepath = r'D:\ms\manager_1640133606904.csv'
        self.holdingcsv_filepath = r'D:\ms\holding_1639356003699.csv'

    def get_white(self):
        '''
        获取白名单 ISIN==MS_SECID
        '''
        id = []
        with open('white_all_162.txt', 'r', encoding='utf-8')as f:
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


    def read_manager_csv(self):
        manager_csv_dic = {}
        with open(self.managercsv_filepath, 'r', encoding='utf-8') as f:
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
            print(manager_csv_dic)
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
        csv_data = self.read_manager_csv()
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
                # SecurityName,weighting 对应位置
                xml_basicInfo_basicInfoDetail = re.findall('<basicInfo>(.*?)</basicInfo>', xml_basicInfo,re.S)  # 修饰符re.S  使.匹配包括换行在内的所有字符
                #reportdate 对应位置
                xml_basicInfo_date = re.findall("<PortfolioSummary>(.*?)</PortfolioSummary>", xml_basicInfo,re.S)

                if xml_basicInfo:
                    # basicInfoISINCode,securityName,weight
                    basicInfo_list = xml_basicInfo_basicInfoDetail[0]
                    basicInfo_detail = basicInfo_list.split("</basicInfoDetail>")
                    # reportDate
                    basicInfo_list_date = xml_basicInfo_date[0]
                    basicInfo_detail_date = basicInfo_list_date.split("</PortfolioSummary>")
                    # print(len(basicInfo_detail))
                    for m in basicInfo_detail:
                        xml_list_detail = []
                        # 持仓占比
                        Weighting = re.findall("<Weighting>(.*?)</Weighting>",m)
                        # weight_list = []
                        if Weighting:
                            print(f"Weighting",Weighting[0])
                            xml_list_detail.append(Weighting[0])
                            # xml_list_detail.sort(key=lambda x:int(x[0]), reverse=True)
                            # weight_top10 = xml_list_detail[0:10]
                            # xml_list_detail.append(weight_top10)

                            # 持仓对应ISIN
                            basicInfoISINCode = re.findall('<ISIN>(.*?)</ISIN>', m)
                            if basicInfoISINCode:
                                print(f"basicInfoISINCode:", basicInfoISINCode[0])
                                xml_list_detail.append(basicInfoISINCode[0])
                            # 名称
                            SecurityName = re.findall("<SecurityName>(.*?)</SecurityName>",m)
                            if SecurityName:
                                print(f"SecurityName",SecurityName[0])
                                xml_list_detail.append(SecurityName[0])
                            for d in basicInfo_detail_date:
                                # 报告日期
                                reportDate = re.findall("<Date>(.*?)</Date>",d)
                                print(f"reportDate",reportDate[0])
                                xml_list_detail.append(reportDate[0])
                            print("=============================")

                        if xml_list_detail:
                            xml_list_detail.append(ISIN)
                            # xml_list_detail.sort()
                            xml_list.append(xml_list_detail)

            print(xml_list)
        return xml_list







if __name__ == '__main__':
    c = Comparexml()

    # c.xml_manager()

    # # 校验manager.csv
    c.compare_manager()

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

    endtime = datetime.now()
    print("RunTime: {}h-{}m-{}s".format(endtime.hour-starttime.hour, endtime.minute-starttime.minute, endtime.second-starttime.second))