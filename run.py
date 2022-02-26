from src.service.spider.talos import talosSpider
from src.service.spider.exploitdb import exploitdbSpider
from src.service.spider.expku import expkuSpider
from src.service.spider.packetstorm import packetstormSpider
from src.service.spider.seclists_org_bugtraq import seclistBugtraqSpider
from src.api.database import SessionLocal

from src.api import service

db = SessionLocal()


def run_spider():
    dict_source_spider = {'exploitdb': exploitdbSpider, 'expku': expkuSpider,
                          'packetstorm': packetstormSpider, 'seclist-Bugtraq': seclistBugtraqSpider,'talos':talosSpider}

    report_dict = {}
    for source, spider in dict_source_spider.items():
        print(source)
        try:
            report_dict[source] = spider.get_update_reports()
        except Exception as ex:
            print(ex)

    for source, reports in report_dict.items():
        for report in reports:
            service.process_report(report, db, source)
