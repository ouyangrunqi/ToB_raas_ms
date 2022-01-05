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
        self.headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36'}
        self.managercsv_filepath = r'D:\ms\manager_debug.csv'


    def get_white(self):
        '''
        获取白名单 ISIN==MS_SECID
        '''
        id = []
        with open('KYG.txt', 'r', encoding='utf-8')as f:
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


    def xml_manager(self):
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
                xml_managers = res.text
                xml_manager = re.findall('<ManagerList>(.*?)</ManagerList>', xml_managers, re.S)  # 修饰符re.S  使.匹配包括换行在内的所有字符
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
                                # print(f"manager_id:", manager_id[0])
                                xml_list_detail.append(manager_id[0])
                                data = requests.get(url=url, headers=self.headers)
                                selector = etree.XML(data.content)
                                xml_MultilingualVariation = selector.xpath(f'//MultilingualVariation[@_Id="{manager_id[0]}"]/../MultilingualVariation')
                                if xml_MultilingualVariation:
                                    xml_LanguageVariation = selector.xpath('//LanguageVariation[@_LanguageId="0L00000082"]/../LanguageVariation')
                                    if xml_LanguageVariation:
                                        GivenName_cn = selector.xpath(f'//MultilingualVariation[@_Id="{manager_id[0]}"]/LanguageVariation [@_LanguageId="0L00000082"]//GivenName')
                                        FamilyName_cn = selector.xpath(f'//MultilingualVariation[@_Id="{manager_id[0]}"]/LanguageVariation [@_LanguageId="0L00000082"]//FamilyName')
                                        manager_name = FamilyName_cn + GivenName_cn
                                        if manager_name:
                                            # print(f"GivenName:", GivenName_cn[0].text)
                                            # print(f"FamilyName:", FamilyName_cn[0].text)
                                            manager_name = FamilyName_cn[0].text + GivenName_cn[0].text
                                            xml_list_detail.append(manager_name)
                                        else:
                                            GivenName_en = re.findall("<GivenName>(.*?)</GivenName>", m)
                                            FamilyName_en = re.findall("<FamilyName>(.*?)</FamilyName>", m)
                                            # print(f"GivenName:", GivenName_en[0])
                                            # print(f"FamilyName:", FamilyName_en[0])
                                            manager_name = GivenName_en[0] + ' ' + FamilyName_en[0]
                                            xml_list_detail.append(manager_name)
                                    else:
                                        GivenName_en = re.findall("<GivenName>(.*?)</GivenName>", m)
                                        FamilyName_en = re.findall("<FamilyName>(.*?)</FamilyName>", m)
                                        # print(f"GivenName:", GivenName_en[0])
                                        # print(f"FamilyName:", FamilyName_en[0])
                                        manager_name = GivenName_en[0] + ' ' + FamilyName_en[0]
                                        xml_list_detail.append(manager_name)
                                else:
                                    GivenName_en = re.findall("<GivenName>(.*?)</GivenName>", m)
                                    FamilyName_en = re.findall("<FamilyName>(.*?)</FamilyName>", m)
                                    # print(f"GivenName:", GivenName_en[0])
                                    # print(f"FamilyName:", FamilyName_en[0])
                                    manager_name = GivenName_en[0] + ' ' + FamilyName_en[0]
                                    xml_list_detail.append(manager_name)

                            # 基金经理任期(管理起始日期)
                            managerStartDate = re.findall("<StartDate>(.*?)</StartDate>", m)
                            if managerStartDate:
                                # print(f"managerStartDate:", managerStartDate[0])
                                xml_list_detail.append(managerStartDate[0])
                            else:
                                pass
                                # print("缺少managerStartDate")
                            # print("=============================")
                        else:
                            pass
                        if xml_list_detail:
                            xml_list_detail.append(ISIN)
                            xml_list_detail.sort()
                            xml_list.append(xml_list_detail)

            # print(xml_list)
        return xml_list


    def read_manager_csv(self):
        manager_csv_dic = {}
        with open(self.managercsv_filepath, 'r') as f:
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


if __name__ == '__main__':
    c = Comparexml()


    # 校验manager.csv
    c.compare_manager()


    endtime = datetime.now()
    print("RunTime: {}h-{}m-{}s".format(endtime.hour-starttime.hour, endtime.minute-starttime.minute, endtime.second-starttime.second))