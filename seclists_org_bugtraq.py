from typing import List

import requests
from htutil import file
from lxml import etree
from lxml.html.clean import Cleaner

from src.util import path
from .BaseSpider import BaseSpider


class SeclistBugtraqSpider(BaseSpider):
    def __init__(self) -> None:
        self.cleaner = Cleaner(
            style=True,
            scripts=True,
            javascript=True,
            remove_tags=frozenset(['pre', 'div'])
        )
        self.session = requests.session()

    def get_new_urls(self) -> List[str]:
        if path.file_spider_bugtraq_url.exists():
            old_urls = file.read_lines(path.file_spider_bugtraq_url)
        else:
            old_urls = []

        html = requests.get('https://seclists.org/bugtraq/').text
        # file.write_text('1.html', html)
        # html = file.read_text('1.html')

        html = etree.HTML(html)

        urls = []

        xpath_list = ['/html/body/table[2]/tr[1]/td[2]/table/tr/td/table/tr[*]/td[*]/a',
                      '/html/body/table[2]/tr[1]/td[2]/table/tr/td/table/tr[*]/td[*]/strong/a']
        for xpath in xpath_list:
            elements = html.xpath(xpath)

            for element in elements:
                href = element.attrib['href']
                index = int(element.text)
                for i in range(index):
                    url = 'https://seclists.org' + \
                        href.replace('/index.html', '') + '/' + str(i)
                    urls.append(url)

        new_urls = list(set(urls) - set(old_urls))
        file.write_text(path.file_spider_bugtraq_url, urls)
        return new_urls

    def request_html(self, url: str) -> str:
        print(f'downloading {url}')
        while True:
            try:
                response = self.session.get(
                    url, allow_redirects=False, timeout=5)
                break
            except Exception:
                pass

        if response.status_code == 200:
            return response.text
        elif response.status_code == 302:
            return '302' + response.text
        else:
            print('--- bugtraq error ---')
            print(url)
            print(response.status_code)
            print(response.text)
            print('--- end ---')

    def clean(self, html: str) -> str:
        raw_html = html
        html = etree.HTML(html)
        pres = html.xpath('//pre')

        if len(pres) != 1:
            return raw_html

        # title
        title = html.xpath('//title/text()')[0].replace('Bugtraq: ', '')
        body = pres[0]
        body_html = etree.tostring(body).decode('utf8')
        body_html = self.cleaner.clean_html(body_html)
        body_html = body_html.replace('</div>', '').replace('<div>', '')

        new_lines = []
        lines = body_html.split('\n')
        for line in lines:
            if len(line) > 0:
                new_lines.append(line)

        text = '\n'.join(new_lines)
        # add title to text
        return title + '\n\n' + text

    def get_update_reports(self):
        new_urls = self.get_new_urls()
        report_list = []
        for url in new_urls:
            # 请求html
            report = self.request_html(url)
            # 清洗html内容
            report = self.clean(report)
            report_list.append(report)
        return report_list


seclistBugtraqSpider = SeclistBugtraqSpider()
