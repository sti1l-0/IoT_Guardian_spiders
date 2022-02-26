import requests
from htutil import file
from lxml import etree
import time
from datetime import datetime, timedelta
from src.util.path import file_spider_packetstorm_date
from .BaseSpider import BaseSpider


class PacketstormSpider(BaseSpider):
    def __init__(self) -> None:
        super().__init__()
        self.sess = requests.session()
        # 加一个list和url的映射关系表
        self.title_dict = {}

    def get_new_urls(self):
        if file_spider_packetstorm_date.exists():
            last_date = file.read_text(file_spider_packetstorm_date)
        else:
            last_date = (datetime.now() - timedelta(days=7)
                         ).strftime('%Y-%m-%d')

        date = datetime.strptime(last_date, '%Y-%m-%d')

        new_urls = []

        while True:
            date_str = date.strftime("%Y-%m-%d")

            xml = self.sess.get(
                f'https://rss.packetstormsecurity.com/files/dates/{date_str}').text
            xml = etree.XML(xml.encode('utf8'))
            for i in xml.xpath('/rss/channel/item[*]'):
                title = i[0]
                url = i[1].text.replace('files/', 'files/download/')
                self.title_dict[url] = title
            url_list = self.title_dict.keys()
            ''' 这里用title_dict替代，应该不会出问题
            link_list = xml.xpath('/rss/channel/item[*]/link/text()')
            url_list = [url.replace('files/', 'files/download/')
                        for url in link_list if url.endswith('.txt')]
            '''
            new_urls.extend(url_list)
            if date_str == time.strftime("%Y-%m-%d"):
                break
            date = date + timedelta(days=1)

        file.write_text(file_spider_packetstorm_date,
                        datetime.now().strftime('%Y-%m-%d'))

        return new_urls
    
    def url2title(self, url:str)->str:
        return self.title_dict[url]

    def request_report(self, url):
        print(f'downloading {url}')
        # 这里用\n\n把标题和内容隔开
        return self.url2title(url) + '\n' + self.sess.get(url).text

    def get_update_reports(self):
        urls = self.get_new_urls()
        report_list = []
        for url in urls:
            try:
                report = self.request_report(url)
                report_list.append(report)
            except Exception as ex:
                print(ex)
        return report_list


packetstormSpider = PacketstormSpider()
