from typing import List
from htutil import file
from src.util.path import *
from .BaseSpider import BaseSpider
from src.util import path

import requests
from htutil import file
from lxml import etree

headers = {
    'authority': 'talosintelligence.com',
    'pragma': 'no-cache',
    'cache-control': 'no-cache',
    'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
    'sec-ch-ua-mobile': '?0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-user': '?1',
    'sec-fetch-dest': 'document',
    'referer': 'https://talosintelligence.com/vulnerability_reports'
}


class TalosSpider(BaseSpider):
    def get_current_url_list(self) -> List[str]:
        """ 获取现在所有报告的 URL

        Returns:
            List[str]: 报告列表的URL
        """
        response = requests.get(
            'https://talosintelligence.com/vulnerability_reports', headers=headers)
        html = etree.HTML(response.text)
        nodes = html.xpath('//*[@id="vul-report"]/tbody/tr[*]/td/a/@href')
        nodes = list(set(nodes))
        nodes = sorted(nodes)
        nodes = ['https://talosintelligence.com' + node for node in nodes]
        return nodes

    def get_one_report(self, url: str) -> str:
        """ 获取一个报告

        Args:
            url (str): 报告 URL

        Returns:
            str: 报告内容
        """
        response = requests.get(url)
        html = response.text
        html = etree.HTML(html)
        nodes = html.xpath("//div[contains(@class, 'report')]")
        if len(nodes) >= 1:
            text = etree.tostring(nodes[0]).decode('utf-8')
        else:
            text = response.text
        return text

    def get_update_reports(self):
        if path.file_spider_talos_url.exists():
            old_urls = file.read_lines(path.file_spider_talos_url)
        else:
            old_urls = []

        report_list = []

        current_urls = self.get_current_url_list()
        for url in current_urls:
            if url not in old_urls:
                report = self.get_one_report(url)
                file.write_text('1.txt', report)
                report_list.append(report)
                file.append_text(path.file_spider_talos_url, url)

        return report_list


talosSpider = TalosSpider()
