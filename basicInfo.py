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
        self.basciInfo_filepath = r'D:\ToB_raas_ms\csv\basicInfo_debug.csv'
        self.white_filepath = r'D:\ToB_raas_ms\white\white_v6.xlsx'


    def get_white(self):
        '''
        获取白名单 ISIN==MS_SECID
        '''
        id = []
        with open('D:\ToB_raas_ms\white\LU.txt', 'r', encoding='utf-8')as f:
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
        white_dic = {}
        region_dic = {}
        fundIndustry_dic = {}
        fundInvestType_dic = {}

        for i in range(1, rowNum):
            white_list = []
            for j in range(colNum):
                white_list.append(Data_sheet.cell_value(i, j))
            region_dic[white_list[1]] = white_list[-1]
            fundIndustry_dic[white_list[1]] = white_list[-2]
            fundInvestType_dic[white_list[1]] = white_list[-3]

        # print(f'基金类型_基金分类白名单: \n\t{fundInvestType_dic}')
        # print(f'地区分类_基金分类白名单: \n\t{region_dic}')
        # print(f'行业分类_基金分类白名单: \n\t{fundIndustry_dic}')

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
                region_dic[k] = "0"
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
                fundIndustry_dic[k] = "0"
        # print('行业分类_basicinfo:\n\t', fundIndustry_dic)
        xlsx_list.append(fundIndustry_dic)

        # print(f'\nxlsx_list:\n\t',xlsx_list)
        return xlsx_list


    def xml_basicInfo(self):
        xml_list = []
        id_list = self.get_white()
        for m in id_list:
            m = m.split('==')
            ISIN = m[0]
            MS_SECID = m[1]

            # url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS"

            url = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnum2022&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=1471&Currencies=BAS&Obsolete=1"

            # basicInfo
            # fundFactSheet-基金月报  fundStatement-基金章程  fundAnnualReport-年度报告  fundInterimReport-中期报告  fundProspectus-基金说明书
            # url2 = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnumhk&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=512&Currencies=BAS&from=from_parent_mindnote" # 下载的文档有水印

            url2 = f"https://edw.morningstar.com/DataOutput.aspx?Package=EDW&ClientId=magnum2022&Id={MS_SECID}&IDTYpe=FundShareClassId&Content=512&Currencies=BAS"  # 用sunrui的账号无水印
            res = requests.get(url)

            if res.status_code == 200:
                print(f">>>>>>>>>>开始获取'{MS_SECID}'的数据>>>>>>>>>>")
                xml_basicInfo = res.text
                xml_basicInfo_FundShareClass = re.findall('<FundShareClass .*?>(.*?)</FundShareClass>', xml_basicInfo,re.S)  # 修饰符re.S  使.匹配包括换行在内的所有字符
                # fundNameEN
                xml_basicInfo_Operation = re.findall('<Operation>(.*?)</Operation>', xml_basicInfo,re.S)
                # baseCurrency,基金信息板块下展示该币种
                xml_basicInfo_PerformanceId = re.findall('<PerformanceId>(.*?)</PerformanceId>', xml_basicInfo, re.S)
                # 基金市场状态  0-停止  1-开放期  2-募集期
                xml_basicInfo_Status = re.findall(f'<FundShareClass _Id="{MS_SECID}" _FundId=".*?" _Status="(.*?)">',xml_basicInfo,re.S)

                if xml_basicInfo:
                    basicInfo_list = xml_basicInfo_FundShareClass[0]
                    basicInfo_list_Operation = xml_basicInfo_Operation[0]
                    basicInfo_list_PerformanceId = [c for c in xml_basicInfo_PerformanceId if "CurrencyId" in c]
                    basicInfo_FundShareClass = basicInfo_list.split("</FundShareClass>")
                    basicInfo_ShareClassBasics =basicInfo_list_Operation.split("</LegalName>")
                    basicInfo_PerformanceId = basicInfo_list_PerformanceId[0]
                    # shareClassCurrency,除基金信息板块外其他页面展示这个币种
                    basicInfo_shareClassCurrency = basicInfo_list_Operation.split("</Currency>")

                    for m in basicInfo_FundShareClass:
                        xml_list_detail = []
                        # 父基金编码
                        parentCode = re.findall('<Fund _Id="(.*?)"',m)
                        if parentCode:
                            # print(f"parentCode:",parentCode[0])
                            xml_list_detail.append(parentCode[0])
                        for name in basicInfo_ShareClassBasics:
                            fundNameEN = re.findall("<LegalName>(.*)",name)
                            if fundNameEN:
                                # print(f"fundNameEN:", fundNameEN[0])
                                x = fundNameEN[0]
                                xml_list_detail.append(x.replace('&amp;', '&'))

                        data = requests.get(url=url, headers=self.headers)
                        date2 = requests.get(url=url2, headers=self.headers)
                        selector = etree.XML(data.content)
                        selector2 = etree.XML(date2.content)

                        # xml_MultilingualVariation = selector.xpath(f'//MultilingualVariation[@_Id="{MS_SECID}"]/../MultilingualVariation')
                        # if xml_MultilingualVariation:
                        #     xml_LanguageVariation = selector.xpath('//LanguageVariation[@_LanguageId="0L00000082"]/../LanguageVariation')
                        #     if xml_LanguageVariation:
                        fundNameSC_1 = selector.xpath(
                            f'/FundShareClass/MultilingualVariation/LanguageVariation[@_LanguageId="0L00000082"]/RegionVariation/Name')
                        fundNameSC_2 = selector.xpath(
                            f'/FundShareClass/Fund/MultilingualVariation/LanguageVariation[@_LanguageId="0L00000082"]/RegionVariation/Name')
                        if fundNameSC_1:
                            # print(f"fundNameSC:", fundNameSC_1[0].text)
                            x = fundNameSC_1[0].text
                            xml_list_detail.append(x.replace(u'\xa0', u'?'))
                        elif fundNameSC_2:
                            x = fundNameSC_2[0].text
                            # print(f"fundNameSC:", fundNameSC_2[0].text)
                            xml_list_detail.append(x.replace(u'\xa0', u'?'))
                        else:
                            # print(f"fundNameSC:无数据")
                            xml_list_detail.append("")

                        baseCurrency = re.findall("<CurrencyId>(.*)</CurrencyId>",basicInfo_PerformanceId)
                        if baseCurrency:
                            # print(f"baseCurrency:", baseCurrency[0])
                            xml_list_detail.append(baseCurrency[0])
                        for Currency in basicInfo_shareClassCurrency:
                            shareClassCurrency = re.findall('<Currency _Id="(.*?)">',Currency)
                            if shareClassCurrency:
                                # print(f"shareClassCurrency:", shareClassCurrency[0])
                                xml_list_detail.append(shareClassCurrency[0])
                        fundStatus = xml_basicInfo_Status[0]

                        ID = f'{ISIN}'
                        # 行业分类
                        dict1 = self.read_xlsx()[2]
                        if ID in dict1:
                            for k, v in dict1.items():
                                if k == ID:
                                    # print(f"fundIndustry:", v)
                                    xml_list_detail.append(v)
                        else:
                            # print(f'fundIndustry:"{MS_SECID}"在white_v6中缺少fundIndustry')
                            xml_list_detail.append("white_v6中缺少fundIndustry")

                        fundStatus = xml_basicInfo_Status[0]
                        if fundStatus:
                            # print(f"fundStatus:", fundStatus[0])
                            xml_list_detail.append(fundStatus[0])

                        # 地区分类
                        dict2 = self.read_xlsx()[1]
                        if ID in dict2:
                            for k, v in dict2.items():
                                    if k == ID:
                                        # print(f"fundRegion:", v)
                                        xml_list_detail.append(v)
                        else:
                            # print(f'fundRegion:"{MS_SECID}"在white_v6中缺少fundRegion')
                            xml_list_detail.append("white_v6中缺少fundRegion")

                        # 基金类型
                        dict3 = self.read_xlsx()[0]
                        if ID in dict3:
                            for k, v in dict3.items():
                                    if k == ID:
                                        # print(f"fundInvestType:", v)
                                        xml_list_detail.append(v)
                        else:
                            # print(f'fundInvestType:"{MS_SECID}"在white_v6中缺少fundInvestType')
                            xml_list_detail.append("white_v6中缺少fundInvestType")





                        # 一年夏普比例
                        sharpeRatioM12 = selector.xpath(f"/FundShareClass/ClassPerformance/Performance/TrailingPerformance[@Type='1000']/RiskAndRating/RiskAnalysis/RiskMeasures/RiskMeasuresDetail[@TimePeriod='M12' and @Type='61']/SharpeRatio")
                        if sharpeRatioM12:
                            # print(f"sharpeRatioM12:", (sharpeRatioM12[0].text).rstrip("0"))
                            xml_list_detail.append((sharpeRatioM12[0].text).rstrip("0"))
                        else:
                            # print(f"sharpeRatioM12: 数据缺失")
                            xml_list_detail.append("")

                        # 三年夏普比例
                        sharpeRatioM36 = selector.xpath(f"/FundShareClass/ClassPerformance/Performance/TrailingPerformance[@Type='1000']/RiskAndRating/RiskAnalysis/RiskMeasures/RiskMeasuresDetail[@TimePeriod='M36' and @Type='61']/SharpeRatio")
                        if sharpeRatioM36:
                            # print(f"sharpeRatioM36:", (sharpeRatioM36[0].text).rstrip("0"))
                            xml_list_detail.append((sharpeRatioM36[0].text).rstrip("0"))
                        else:
                            # print(f"sharpeRatioM36: 数据缺失")
                            xml_list_detail.append("")

                        # 最大一年回撤
                        maxDrawdownM12 = selector.xpath(
                            f"/FundShareClass/ClassPerformance/Performance/TrailingPerformance[@Type='1000']/RiskAndRating/RiskAnalysis/RiskMeasures/RiskMeasuresDetail[@TimePeriod='M12' and @Type='61']/MaximumDrawdown")
                        if maxDrawdownM12:
                            # print(f"maxDrawdownM12:", maxDrawdownM12[0].text)
                            xml_list_detail.append(str(round(float(maxDrawdownM12[0].text)/100, 4)))
                        else:
                            # print(f"maxDrawdownM12: 数据缺失")
                            xml_list_detail.append("")

                        # 最大三年回撤
                        maxDrawdownM36 = selector.xpath(
                            f"/FundShareClass/ClassPerformance/Performance/TrailingPerformance[@Type='1000']/RiskAndRating/RiskAnalysis/RiskMeasures/RiskMeasuresDetail[@TimePeriod='M36' and @Type='61']/MaximumDrawdown")
                        if maxDrawdownM36:
                            # print(f"maxDrawdownM36:", maxDrawdownM36[0].text)
                            xml_list_detail.append(str(round(float(maxDrawdownM36[0].text)/100, 4)))
                        else:
                            # print(f"maxDrawdownM36: 数据缺失")
                            xml_list_detail.append("")

                        # 一年波幅
                        standardDeviationM12 = selector.xpath(
                            f"/FundShareClass/ClassPerformance/Performance/TrailingPerformance[@Type='1000']/RiskAndRating/RiskAnalysis/RiskMeasures/RiskMeasuresDetail[@TimePeriod='M12' and @Type='61']/StandardDeviation")
                        if standardDeviationM12:
                            # print(f"standardDeviationM12:", standardDeviationM12[0].text)
                            xml_list_detail.append(str(round(float(standardDeviationM12[0].text)/100, 4)))
                        else:
                            # print(f"standardDeviationM12: 数据缺失")
                            xml_list_detail.append("")

                        # 三年波幅
                        standardDeviationM36 = selector.xpath(
                            f"/FundShareClass/ClassPerformance/Performance/TrailingPerformance[@Type='1000']/RiskAndRating/RiskAnalysis/RiskMeasures/RiskMeasuresDetail[@TimePeriod='M36' and @Type='61']/StandardDeviation")
                        if standardDeviationM36:
                            # print(f"standardDeviationM36:", standardDeviationM36[0].text)
                            xml_list_detail.append(str(round(float(standardDeviationM36[0].text)/100, 4)))
                        else:
                            # print(f"standardDeviationM36: 数据缺失")
                            xml_list_detail.append("")
                        # else:
                            # if standardDeviationM12:
                            #     print(f"standardDeviationM36:", standardDeviationM12[0].text)
                            #     xml_list_detail.append(str(round(float(standardDeviationM12[0].text)/100, 4)))
                            # else:
                            #     print(f"standardDeviationM12 & standardDeviationM36: 数据缺失")
                            #     xml_list_detail.append("standardDeviationM12 & standardDeviationM36: N/A")

                        """
                        分红频率 取最新一条
                        dividendFrequencyType 
                        
                            A$-Annually
                            a$-Semi-Annually
                            B$-Bi-Monthly
                            D$-Daily
                            M$-Monthly
                            m$-Semi-Monthly
                            N$-None
                            Q$-Quarterly
                            W$-Weekly 
                        
                        """

                        # 股息率：
                        dividendYield = selector.xpath('//EquityStyleFactor//ProspectiveDividendYield')
                        if dividendYield:
                            # print(f"dividendYield:", dividendYield[0].text)
                            xml_list_detail.append(dividendYield[0].text)
                        else:
                            # print("dividendYield:货币基金无此字段,部分债券基金没有")
                            xml_list_detail.append("")

                        # 最新股息率
                        latestDividendYield = selector.xpath('//EquityStatistics//DividendYield')
                        if latestDividendYield:
                            # print(f"latestDividendYield:", latestDividendYield[0].text)
                            xml_list_detail.append(latestDividendYield[0].text)
                        else:
                            # print("latestDividendYield:货币基金无此字段,部分债券基金没有")
                            xml_list_detail.append("")

                        # 晨星星级
                        msRating = selector.xpath("/FundShareClass/ClassPerformance/Performance/TrailingPerformance/RiskAndRating/StarRating/RatingDetail[@TimePeriod='M36' and @Type='81']/Rating/Value")

                        if msRating:
                            # print(f"msRating:", msRating[0].text)
                            xml_list_detail.append(msRating[0].text)
                        else:
                            # print(f"msRating: 缺少数据")
                            xml_list_detail.append("")

                        # # 基金规模
                        # fundAssetsSize = selector.xpath('/FundShareClass/Fund/HistoricalOperation/LatestNetAsset/Value')
                        # if fundAssetsSize:
                        #     print(f"fundAssetsSize:", fundAssetsSize[0].text)
                        #     xml_list_detail.append(fundAssetsSize[0].text)

                        # 成立时间
                        fundSetupDate = selector.xpath('/FundShareClass/Operation/ShareClassBasics/InceptionDate')
                        if fundSetupDate:
                            # print(f"fundSetupDate:", fundSetupDate[0].text)
                            xml_list_detail.append(fundSetupDate[0].text)

                        # 起投金额
                        minInitialInvestment = selector.xpath(f'//PurchaseDetail [@_CurrencyId="{baseCurrency[0]}"]//InitialInvestment')
                        if minInitialInvestment:
                            # print(f"minInitialInvestment:", minInitialInvestment[0].text)
                            xml_list_detail.append(minInitialInvestment[0].text)
                        else:
                            # print(f"minInitialInvestment: 无起投金额")
                            xml_list_detail.append("")

                        # 最小追加金额
                        minSubsequentInvestment = selector.xpath(f'//PurchaseDetail [@_CurrencyId="{baseCurrency[0]}"]//SubsequentInvestment [@_Unit="1"]')
                        if minSubsequentInvestment:
                            # print(f"minSubsequentInvestment:", minSubsequentInvestment[0].text)
                            xml_list_detail.append(minSubsequentInvestment[0].text)
                        else:
                            # print(f"minSubsequentInvestment: 无最小追加金额")
                            xml_list_detail.append("")

                        # 基金管理公司名称-EN
                        fundManagementCompanyEN = selector.xpath('/FundShareClass/Fund/FundManagement/ProviderCompany/Company/CompanyOperation/CompanyBasics/Name')
                        if fundManagementCompanyEN:
                            # print(f"fundManagementCompanyEN:", fundManagementCompanyEN[0].text)
                            xml_list_detail.append(fundManagementCompanyEN[0].text)
                        else:
                            xml_list_detail.append("")

                        # 基金管理公司名称-SC
                        fundManagementCompanySC = selector.xpath('//CompanyOperation//LanguageVariation[@_LanguageId="0L00000082"]/RegionVariation/Name')
                        if fundManagementCompanySC:
                            # print(f"fundManagementCompanySC:", fundManagementCompanySC[0].text)
                            xml_list_detail.append(fundManagementCompanySC[0].text)
                        else:
                            xml_list_detail.append("")

                        # 投资目标简述
                        fundInvestObject = selector.xpath('//ShareClassNarratives[@_LanguageId="0L00000122"]/KIIDObjective')
                        if fundInvestObject:
                            # print(f"fundInvestObject:", fundInvestObject[0].text)
                            xml_list_detail.append(fundInvestObject[0].text)
                        else:
                            # print(f"fundInvestObject: 缺少fundInvestObject")
                            xml_list_detail.append("")

                        # 基金投资策略简述-EN
                        fundInvestStrategyEN = selector.xpath('//FundNarratives[@_LanguageId="0L00000122"]//InvestmentStrategy')
                        if fundInvestStrategyEN:
                            x = fundInvestStrategyEN[0].text
                            # print(f"fundInvestStrategyEN:", fundInvestStrategyEN[0].text)
                            xml_list_detail.append(x.replace('\n', ' '))
                        else:
                            # print(f"fundInvestStrategyEN: 无数据")
                            xml_list_detail.append("")

                        # 基金投资策略简述-SC
                        fundInvestStrategySC = selector.xpath('//FundNarratives[@_LanguageId="0L00000082"]//InvestmentStrategy')
                        if fundInvestStrategySC:
                            # print(f"fundInvestStrategySC:", fundInvestStrategySC[0].text)
                            x = fundInvestStrategySC[0].text
                            xml_list_detail.append(x.replace('\n', ''))
                        else:
                            # print(f"fundInvestStrategySC: 无数据")
                            xml_list_detail.append("")

                        # 基金月报
                        fundFactSheet_cn = selector2.xpath(
                            f"/FundShareClass/ProprietaryData/LatestDocuments/DocumentType[@_Type='52']/Document[@Market='HKG' and @LanguageId='0L00000082']")
                        fundFactSheet_en = selector2.xpath(
                            f"/FundShareClass/ProprietaryData/LatestDocuments/DocumentType[@_Type='52']/Document[@Market='HKG' and @LanguageId='0L00000122']")
                        if fundFactSheet_cn:
                            # print(f"fundFactSheet_cn:", fundFactSheet_cn[0].text)
                            xml_list_detail.append(fundFactSheet_cn[0].text)
                        elif fundFactSheet_en:
                            # print(f"fundFactSheet_en:", fundFactSheet_en[0].text)
                            xml_list_detail.append(fundFactSheet_en[0].text)
                        else:
                            # print(f"fundFactSheet: N/A")
                            xml_list_detail.append("N/A")


                        # 基金章程
                        fundStatement_cn = selector2.xpath(
                            f"/FundShareClass/ProprietaryData/LatestDocuments/DocumentType[@_Type='76']/Document[@Market='HKG' and @LanguageId='0L00000082']")
                        fundStatement_en = selector2.xpath(
                            f"/FundShareClass/ProprietaryData/LatestDocuments/DocumentType[@_Type='76']/Document[@Market='HKG' and @LanguageId='0L00000122']")
                        if fundStatement_cn:
                            # print(f"fundStatement_cn:", fundStatement_cn[0].text)
                            xml_list_detail.append(fundStatement_cn[0].text)
                        elif fundStatement_en:
                            # print(f"fundStatement_en:", fundStatement_en[0].text)
                            xml_list_detail.append(fundStatement_en[0].text)
                        else:
                            # print(f"fundStatement: N/A")
                            xml_list_detail.append("N/A")

                        # 年度报告
                        fundAnnualReport_cn = selector2.xpath(
                            f"/FundShareClass/ProprietaryData/LatestDocuments/DocumentType[@_Type='4']/Document[@Market='HKG' and @LanguageId='0L00000082']")
                        fundAnnualReport_en = selector2.xpath(
                            f"/FundShareClass/ProprietaryData/LatestDocuments/DocumentType[@_Type='4']/Document[@Market='HKG' and @LanguageId='0L00000122']")
                        if fundAnnualReport_cn:
                            # print(f"fundAnnualReport_cn:", fundAnnualReport_cn[0].text)
                            xml_list_detail.append(fundAnnualReport_cn[0].text)
                        elif fundAnnualReport_en:
                            # print(f"fundAnnualReport_en:", fundAnnualReport_en[0].text)
                            xml_list_detail.append(fundAnnualReport_en[0].text)
                        else:
                            # print(f"fundAnnualReport: N/A")
                            xml_list_detail.append("N/A")

                        # 中期报告
                        fundInterimReport_cn = selector2.xpath(
                            f"/FundShareClass/ProprietaryData/LatestDocuments/DocumentType[@_Type='5']/Document[@Market='HKG' and @LanguageId='0L00000082']")
                        fundInterimReport_en = selector2.xpath(
                            f"/FundShareClass/ProprietaryData/LatestDocuments/DocumentType[@_Type='5']/Document[@Market='HKG' and @LanguageId='0L00000122']")
                        if fundInterimReport_cn:
                            # print(f"fundInterimReport_cn:", fundInterimReport_cn[0].text)
                            xml_list_detail.append(fundInterimReport_cn[0].text)
                        elif fundInterimReport_en:
                            # print(f"fundInterimReport_en:", fundInterimReport_en[0].text)
                            xml_list_detail.append(fundInterimReport_en[0].text)
                        else:
                            # print(f"fundInterimReport: N/A")
                            xml_list_detail.append("N/A")

                        # 基金说明书
                        fundProspectus_cn = selector2.xpath(
                            f"/FundShareClass/ProprietaryData/LatestDocuments/DocumentType[@_Type='1']/Document[@Market='HKG' and @LanguageId='0L00000082']")
                        fundProspectus_en = selector2.xpath(
                            f"/FundShareClass/ProprietaryData/LatestDocuments/DocumentType[@_Type='1']/Document[@Market='HKG' and @LanguageId='0L00000122']")
                        if fundProspectus_cn:
                            # print(f"fundProspectus_cn:", fundProspectus_cn[0].text)
                            xml_list_detail.append(fundProspectus_cn[0].text)
                        elif fundProspectus_en:
                            # print(f"fundProspectus_en:", fundProspectus_en[0].text)
                            xml_list_detail.append(fundProspectus_en[0].text)
                        else:
                            # print(f"fundProspectus: N/A")
                            xml_list_detail.append("N/A")

                        # 收益率同类表现排名-1M
                        peerGroupRankM1 = selector.xpath(f'/FundShareClass/ClassPerformance/Performance/TrailingPerformance/TrailingReturn/Return[@Type="1"]/ReturnDetail[@TimePeriod="M1"]/PeerGroupRank/PeerGroupRankDetail/PercentileRank')
                        if peerGroupRankM1:
                            # print(f"peerGroupRankM1:", peerGroupRankM1[0].text)
                            xml_list_detail.append(peerGroupRankM1[0].text)
                        else:
                            # print(f"peerGroupRankM1: 无数据")
                            xml_list_detail.append("")

                        # 收益率同类表现排名-3M
                        peerGroupRankM3 = selector.xpath(f'/FundShareClass/ClassPerformance/Performance/TrailingPerformance/TrailingReturn/Return[@Type="1"]/ReturnDetail[@TimePeriod="M3"]/PeerGroupRank/PeerGroupRankDetail/PercentileRank')
                        if peerGroupRankM3:
                            # print(f"peerGroupRankM3:", peerGroupRankM3[0].text)
                            xml_list_detail.append(peerGroupRankM3[0].text)
                        else:
                            # print(f"peerGroupRankM3: 无数据")
                            xml_list_detail.append("")

                        # 收益率同类表现排名-6M
                        peerGroupRankM6 = selector.xpath(f'/FundShareClass/ClassPerformance/Performance/TrailingPerformance/TrailingReturn/Return[@Type="1"]/ReturnDetail[@TimePeriod="M6"]/PeerGroupRank/PeerGroupRankDetail/PercentileRank')
                        if peerGroupRankM6:
                            # print(f"peerGroupRankM6:", peerGroupRankM6[0].text)
                            xml_list_detail.append(peerGroupRankM6[0].text)
                        else:
                            # print(f"peerGroupRankM6: 无数据")
                            xml_list_detail.append("")

                        # 收益率同类表现排名-12M
                        peerGroupRankM12 = selector.xpath(f'/FundShareClass/ClassPerformance/Performance/TrailingPerformance/TrailingReturn/Return[@Type="1"]/ReturnDetail[@TimePeriod="M12"]/PeerGroupRank/PeerGroupRankDetail/PercentileRank')
                        if peerGroupRankM12:
                            # print(f"peerGroupRankM12:", peerGroupRankM12[0].text)
                            xml_list_detail.append(peerGroupRankM12[0].text)
                        else:
                            # print(f"peerGroupRankM12: 无数据")
                            xml_list_detail.append("")

                        # 收益率同类表现排名-36M
                        peerGroupRankM36 = selector.xpath(f'/FundShareClass/ClassPerformance/Performance/TrailingPerformance/TrailingReturn/Return[@Type="1"]/ReturnDetail[@TimePeriod="M36"]/PeerGroupRank/PeerGroupRankDetail/PercentileRank')
                        if peerGroupRankM36:
                            # print(f"peerGroupRankM36:", peerGroupRankM36[0].text)
                            xml_list_detail.append(peerGroupRankM36[0].text)
                        else:
                            # print(f"peerGroupRankM36: 无数据")
                            xml_list_detail.append("")

                        # 操作费用比率
                        netExpenseRatio = selector.xpath('//FeeAndExpense/NetExpenseRatio')
                        if netExpenseRatio:
                            x = netExpenseRatio[0].text
                            # print(f"netExpenseRatio:", x)
                            xml_list_detail.append(str(Decimal(x).quantize(Decimal('0.000000'), rounding='ROUND_HALF_UP') / 100).rstrip("0"))
                        else:
                            # print(f"netExpenseRatio: 缺少netExpenseRatio")
                            xml_list_detail.append("")

                        # # 年报日期
                        # annualReportDate = selector.xpath(f"/FundShareClass/Operation/AnnualReport[@_Type='2']/Date")
                        # if annualReportDate:
                        #     print(f"annualReportDate:", annualReportDate[0].text)
                        #     xml_list_detail.append(annualReportDate[0].text)
                        # else:
                        #     xml_list_detail.append("")

                        # 管理费
                        managementFee = selector.xpath(f'/FundShareClass/Operation/Prospectus/ManagementFee/FeeSchedule/Value')
                        if managementFee:
                            x = managementFee[0].text
                            # print(f"managementFee:", x)
                            xml_list_detail.append(str(Decimal(x).quantize(Decimal('0.000000'), rounding='ROUND_HALF_UP') / 100).rstrip("0"))
                        else:
                            xml_list_detail.append("")

                        # categoryId = selector.xpath(f"/FundShareClass[@_Status='1']/Fund/FundBasics/@_CategoryId")
                        # if categoryId:
                        #     print(f"categoryId:", categoryId[0].text)
                        #     xml_list_detail.append(categoryId[0].text)

                        if xml_list_detail:
                            xml_list_detail.append(ISIN)
                            xml_list_detail.sort()
                            xml_list.append(xml_list_detail)

            print(xml_list)
        return xml_list


    def read_basicInfo_csv(self):
        basicInfo_csv_dic = {}
        with open(self.basciInfo_filepath, 'r') as f:
            reader = csv.reader(f)
            i = 0
            for row in reader:
                if i == 0:
                    pass
                else:
                    row = row[0:16] + row[17:20] + row[21:-4] + row[-3:-2]
                    # annualReportDate = row[-2]  # 读取csv中的日期
                    # if "/" in annualReportDate:
                    #     csv_managerStartDate = annualReportDate.split("/")  # csv中，年月日，根据"/"切割
                    #     annualReportDate = self.date_conversion(csv_managerStartDate)  # 把切割后的列表传进日期转换的方法date_conversion()
                    # if "-" in annualReportDate: # 同理，月份1~9加0，日期1~9加0
                    #     csv_managerStartDate = annualReportDate.split("-")
                    #     annualReportDate = self.date_conversion(csv_managerStartDate)
                    # row[-2] = annualReportDate

                    fundSetupDate = row[19]  # 读取csv中的日期
                    if "/" in fundSetupDate:
                        csv_managerStartDate = fundSetupDate.split("/")  # csv中，年月日，根据"/"切割
                        fundSetupDate = self.date_conversion(
                            csv_managerStartDate)  # 把切割后的列表传进日期转换的方法date_conversion()
                    if "-" in fundSetupDate:  # 同理，月份1~9加0，日期1~9加0
                        csv_managerStartDate = fundSetupDate.split("-")
                        fundSetupDate = self.date_conversion(csv_managerStartDate)
                    row[19] = fundSetupDate

                    row.sort()
                    basicInfo_csv_dic[f"第{i}行"] = row
                i += 1
            print(basicInfo_csv_dic)
            return basicInfo_csv_dic


    def compare_basicInfo(self):
        '''
        比较 basicInfo.csv文件
        '''
        times = self.get_time()
        print('\n>>>>>>>>>>正在比较basicInfo.csv文件>>>>>>>>>>')
        basicInfo_list = self.xml_basicInfo()
        # print(basicInfo_list)
        print(f"ms数据量：",len(basicInfo_list))
        csv_data = self.read_basicInfo_csv()
        # print(csv_data)
        print(f"basicInfo.csv数据量：",len(csv_data))

        if len(basicInfo_list) == len(csv_data):
            j = 0
            for k, v in csv_data.items():
                i = 0
                for cm in basicInfo_list:
                    if operator.eq(cm, v):
                        i += 1
                        j += 1
                    else:
                        pass
                # i += 1 # 打印相同数据
                if i != 1:# 数据相同，i计数+1,即相同的数据不写入txt
                    self.write_compare_data('result_basicInfo.txt', k, times)
                    print(f'数据不一致：',k)
            if j == len(basicInfo_list):# 数据比对相同时，j的计数+1，相同数=总数，数据一致。
                print('\nbasicInfo.csv >>>校验通过，数据一致!')
        else:
            print('数据量不一致')
            self.write_compare_data('result_manager.txt', '数据量不一致', times)



if __name__ == '__main__':
    c = Comparexml()
    # 校验basicInfo.csv内容
    c.compare_basicInfo()

    endtime = datetime.now()
    print("\nRunTime: {}h-{}m-{}s".format(endtime.hour-starttime.hour, endtime.minute-starttime.minute, endtime.second-starttime.second))