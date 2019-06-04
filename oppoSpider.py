import redis
import requests
class SanXingSpider(object):
    def __init__(self):
        """
        初始化方法
        """
        self.default = "null"
        # 获取数据库的连接
        self.db = redis.Redis(host='127.0.0.1', port=6379, db=7)
        # 初始url
        self.base_url = ' http://i3.store.nearme.com.cn/client/get_new_search.pb'
        # POST 请求，请求body为xml
        self.data = {
            'brand': 'samsung',
            'rom': '2',
            'desktop': 'desktop_other',
            'locale': 'zh_CN',
            'uid': 'oppo.uid.nearme',
            'Referer': 'OPPO R11 / appstore / 4.3.1 / 355360840230535',
            'User - Agent': 'OPPO + R11 / 4.4.2 / Market / 4.3.1',
            'Connection': 'Keep - Alive',
            'Ext - System': 'OPPO A7X / 4.4.2 / 0 / 2 / 2 / 4.3.1 / 20',
            'Ext - User': '-1 / 355360840230535 / 0',
            'Content - Type': 'application / octet - stream',
            'Accept - Encoding': 'gzip',
            'Screen': '1280# 720',
            'VersionCode': '4310',
            'ImgType': 'webp',
            'Host': 'i3.store.nearme.com.cn',
            'Content - Length': '72'
        }
