import re
import xml
import redis
import requests
from xmltodict import parse
import os
import sys
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(os.path.split(rootPath)[0])
from utils import get_db, RESULT_COLLECTIONS_NAME

"""
三星应用市场数据采集
"""

class SanXingSpider(object):
    def __init__(self):
        """
        初始化方法
        """
        self.default = "null"
        # 获取数据库的连接
        self.db = redis.Redis(host='127.0.0.1', port=6379, db=4,password='pengfeiQDS')
        # 初始url
        self.base_url = 'https://cn-ms.galaxyappstore.com/ods.as?reqId=2040 '
        # 初始url，用于请求APP描述的地址
        self.base_url_2 = 'https://cn-ms.galaxyappstore.com/ods.as?reqId=2281'
        # POST 请求，请求body为xml
        self.body = '<?xml version="1.0" encoding="UTF-8" standalone="yes" ?>' \
                    '<SamsungProtocol networkType="0" version2="0" lang="EN" openApiVersion="19" deviceModel="SM-G955N" mcc="460" mnc="07" csc="WIFI" odcVersion="4.4.01.7" version="5.9" filter="1" odcType="01" systemId="1544146105942">' \
                    '<request name="searchProductListEx2Notc" id="2040" numParam="10" transactionId="70855219082">' \
                    '<param name="qlDeviceType">phone</param>' \
                    '<param name="qlDomainCode">sa</param>' \
                    '<param name="keyword">{}</param>' \
                    '<param name="alignOrder">bestMatch</param>' \
                    '<param name="endNum">30</param>' \
                    '<param name="contentType">all</param>' \
                    '<param name="startNum">1</param>' \
                    '<param name="imgWidth">135</param>' \
                    '<param name="qlInputMethod">iqry</param>' \
                    '<param name="imgHeight">135</param>' \
                    '</request>' \
                    '</SamsungProtocol>'
        # 用于请求商品描述的信息，需要先获取产品的id，传入拼接出请求
        self.body_2 = '<?xml version="1.0" encoding="utf-8" ?>' \
                      '<SamsungProtocol networkType="0" version2="0" lang="EN" openApiVersion="19" deviceModel="SM-G955N" mcc="460" mnc="07" csc="WIFI" odcVersion="4.4.01.7" version="5.9" filter="1" odcType="01" systemId="1544146105942">' \
                      '<request name="productDetailOverview" id="2281" numParam="4" transactionId="70855219082">' \
                      '<param name="screenImgWidth">720</param>' \
                      '<param name="productID">{}</param>' \
                      '<param name="screenImgHeight">1280</param>' \
                      '<param name="orderID"/>' \
                      '</request>' \
                      '</SamsungProtocol>'
    def get_url(self):
        # 获取数据库的连接
        db = self.db
        # 获取所有的关键字总数
        keywords_total = db.dbsize()
        # 遍历获取所有的关键字
        for index in range(720001,840001):
        #for index in range(keywords_total):
            # 获取关键字
            keyword = db.get(str(index)).decode('utf-8')
            # 拼接构造出url
            keyword = (u'%s' % keyword)
            print((keyword.encode("ascii", "xmlcharrefreplace")).decode())
            yield self.body.format((keyword.encode("ascii", "xmlcharrefreplace")).decode())
    def get_page(self,data):
        """
        根据URL，获取响应
        :param url:
        :return:
        """
        page = requests.post(url=self.base_url, data=data, verify=False).text
        print("查看获取的数据结构：===================", page)
        return page
    def parse_page(self,page):
        """
        获取响应，将xml解析，获取目标字段
        这个方法解析数据有点坑需要一级一级的标签去选择，
        目前还没有去查相应的资料去直接选择到位
        :param page:
        :return:
        """
        # 解析page,xml
        try:
            data = parse(page)
            # 获取最外层的标签
            # first = data.get('SamsungProtocol', {})    # 获取最外层的标签，字典形式
            # second = first.get("response", [])   # 获取第二层的标签，列表形式
            # items = second.get("list", [])  # 获取第三层标签，列表形式
            items = data['SamsungProtocol']['response']['list']
            print("查看长度++++++++++++++++++++++++",type(items))
            return items
        except xml.parsers.expat.ExpatError:
            pass
    def get_data_lists(self,items):
        """
        根据获取的APP列表信息获取每一个APP的信息
        :param items: APP列表
        :return:
        """
        # 这儿一步需要判断获取得items是不是一个列表形式，这会直接影响程序是否报错
        if isinstance(items, list):
            # 如果是list对象则可以遍历获取
            for item in items:
                print("查看获取得item:==============================",item)
                # 遍历获取每个APP信息
                values = item.get('value')
                print("查看获得得values:",values)
                if values:
                    yield values
        else:
            try:
                values = items.get('value')
                print("检查是否获取正确的values：=================================",values)
                if values:
                    yield values
            except AttributeError:
                pass

    def get_data(self,values):
        """
        获取每一个APP，将获取的键值对儿重新整合成字典形式
        因为上一个函数是生成器，故需要遍历上个函数的返回值
        :param values:
        :return:
        """
        app_des = list()
        app_info = list()
        for value in values:
            app_des.append(value.get("@name"))
            app_info.append(value.get("#text"))
        return dict(zip(app_des, app_info))
    def write_to_file(self, path, data):
        """
        给定路径创建文件
        给定内容将数据写入文件
        :param path: 路径
        :param data: 数据
        :return:
        """
        with open(path, 'a+', encoding='utf-8') as f:
            f.write(data)
    def save_to_mongo(self,data):
        """
        增加方法：将数据存入mongodb数据库中
        """
        if isinstance(data,dict):
            mongo_db = get_db()
            mongo_db[RESULT_COLLECTIONS_NAME].insert(data)
    def get_desc_body(self, id):
        """
        传入商品id,获取APP描述的json
        :param id:
        :return: 拼接后的body
        """
        return self.body_2.format(id)
    def get_desc(self, url, body):
        """
        传入url,获取响应，解析出商品描述信息
        :param url:
        :return:
        """
        page = requests.post(url=url, data=body, verify=False).text
        print(page)
        return page
    def run(self):
        # try:
        urls = self.get_url()
        for url in urls:
            # 获取响应
            try:
                page = self.get_page(url)
                items = self.parse_page(page)
                for values in self.get_data_lists(items):
                    dict_ = self.get_data(values)
                    # 搜索关键字
                    if dict_.get("keyword"):
                        # 创建一个新的字典，用于存储最终结果
                        dd = dict()
                        keyword = dict_.get("keyword")
                        dd['keyword'] = keyword
                        # 获取APP名称
                        if dict_.get("productName"):
                            productName = dict_.get("productName")
                        else:
                            productName = self.default
                        dd['productName'] = productName
                        print("查看APP名称：", productName)
                        # APP开发者
                        if dict_.get("sellerName"):
                            sellerName = dict_.get("sellerName")
                        else:
                            sellerName = self.default
                        dd['sellerName'] = sellerName
                        print("查看APP开发者：", sellerName)
                        # APP图片连接
                        if dict_.get("productImgUrl"):
                            productImgUrl = dict_.get("productImgUrl")
                        else:
                            productImgUrl = self.default
                        dd['productImgUrl'] = productImgUrl
                        print("查看APP图片：", productImgUrl)
                        # APP大小
                        if dict_.get("installSize"):
                            installSize = int(dict_.get("installSize")) / 1024 / 1024
                        else:
                            installSize = self.default
                        dd['installSize'] = installSize
                        print("查看APP大小：", installSize)
                        # APP上线日期
                        if dict_.get("date"):
                            date = dict_.get("date")
                        else:
                            date = self.default
                        dd['date'] = date
                        # APP评分
                        if dict_.get("averageRating"):
                            averageRating = dict_.get("averageRating")
                        else:
                            averageRating = self.default
                        dd['averageRating'] = averageRating  
                        # APP版本
                        if dict_.get("version"):
                            version = dict_.get("version")
                        else:
                            version = self.default
                        dd['version'] = version
                        print("查看APP版本：", version)
                        # APP 产品ID
                        if dict_.get("productID"):
                            productID = dict_.get("productID")
                        print("查看APP的ID:", productID)
                        dd['productID'] = productID
                        # 根据APP 的ID 获取APP描述
                        try:
                            app_desc_ = self.get_desc(url=self.base_url_2, body=self.get_desc_body(productID))
                            datas = parse(app_desc_)['SamsungProtocol']['response']['list']
                            values = datas.get('value')
                            app_desc = [value.get("#text") for value in values][2]
                            app_desc_2 = app_desc.replace('\r\n', "")
                            print("查看获取的数据：===================================",app_desc)
                            print("查看获取的数据2：===================================", app_desc_2)
                            dd['app_desc'] = app_desc_2
                            # 把数据存入 mongo
                            self.save_to_mongo(dd)
                            print("开始存入数据：", dd)
                            # 将获取的目标字段整理成统一格式，定义变量接收拼接的结果
                            #result_content = ""
                            #result_content = result_content.join(
                                #keyword + "ÿ" + productName + "ÿ" + sellerName + "ÿ" + app_desc_2 +
                                #"ÿ" + productImgUrl + "ÿ" + str(installSize) + "M" + "ÿ" + date +
                                #"ÿ" + averageRating + "ÿ" + version + "ÿ" + "\n"
                            #)
                            #self.write_to_file(r'./三星数据.txt', result_content)
                            #self.write_to_file(r'./关键字.txt', keyword + "\n")
                        except :
                            pass
            except:
                pass


if __name__ == "__main__":
    # 创建对象
    sanxingSpider = SanXingSpider()
    # 运行
    sanxingSpider.run()
