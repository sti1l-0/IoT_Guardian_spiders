import re
import requests
from sqlalchemy.sql.expression import text
from .BaseSpider import BaseSpider

from src.util.path import file_spider_expku_date
from htutil import file

from datetime import datetime, timedelta

host = 'http://www.expku.com'


class ExpkuSpider(BaseSpider):
    def __init__(self) -> None:
        super().__init__()
        self.session = requests.session()

    def get_new_urls(self, last_date: str):

        pair = []
        types = ['remote', 'local', 'web', 'dos', 'shellcode']
        for type in types:
            reach_buttom = 0
            last_page = re.search(
                '\d+(?=\.html\S+末页)', self.session.get(host + '/' + type + '/').text).group()
            for i in range(1, int(last_page)):
                weburl = host + '/' + type + '/list_' + \
                    str(types.index(type) + 4) + '_' + str(i) + '.html'
                web = self.session.get(weburl)
                paths = re.findall('/' + type + '/\d*.html', web.text)
                times = re.findall('\d{4}-\d{2}-\d{2}', web.text)
                this_page = list(zip(times, paths[::2]))
                for time, path in this_page:
                    if time >= last_date:
                        pair.append(f'{host}{path}')
                    else:
                        reach_buttom = 1
                        break
                if reach_buttom == 1:
                    break
        return pair

    def download_report(self, url) -> str:
        print(f'downloading {url}')
        html = self.session.get(url)
        try:
            # add title here
            title = re.search('(?<=">).*(?=<\/h1>)', html.text).group()
            poc = re.search(
                '(?<=<pre>)[\S\s]*(?=</pre>)', html.text).group()
        except AttributeError:
            return ''

        report = url + '\n\t' + title + '\n\n' + poc + '\n\n'

        return report

    def get_update_reports(self) -> list:

        if file_spider_expku_date.exists():
            last_date = file.read_text(file_spider_expku_date)
        else:
            last_date = (datetime.now() - timedelta(days=60)
                         ).strftime('%Y-%m-%d')

        print(last_date)
        url_list = self.get_new_urls(last_date)

        report_list = []

        for url in url_list:
            try:
                report = self.download_report(url)
                if len(report) > 0:
                    report_list.append(report)
            except Exception as ex:
                print(ex)
        file.write_text(file_spider_expku_date,
                        datetime.now().strftime('%Y-%m-%d'))

        return report_list


expkuSpider = ExpkuSpider()


def main():
    print(expkuSpider.get_new_urls('2021-05-19'))


if __name__ == '__main__':
    main()
