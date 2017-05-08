import scrapy
from ironman.items import RaceResultItem
import urlparse

class RaceResultsSpider(scrapy.Spider):
    name = "raceresults"
    fields_to_export = ['bib', 'name', 'gender', 'country', 'age_group', 'point', 'overall_rank', 'group_rank', 'gender_rank', 'time_overall', 'time_swim', 'time_bike', 'time_run', 'time_T1', 'time_T2', 'link', 'certificate']

    def __init__(self, category=None, *args, **kwargs):
        super(RaceResultsSpider, self).__init__(*args, **kwargs)
        self.csv_filename = getattr(self, 'filename', None) or 'race_results'
        self.url = getattr(self, 'url', None)
        emailsString = getattr(self, 'emails', None) or ''
        self.emails = [x.strip() for x in emailsString.split(',')]

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse) if self.url is not None else None

    def parse(self, response):
        # count = 0
        for row in response.css('.content-table .race-list tbody tr'):
            detailLink = row.css('::attr(data-result-page)').extract_first()
            # if count == 10:
            #     break
            # count += 1
            item = RaceResultItem({
                'bib': row.css('::attr(data-bib-number)').extract_first().strip(),
                'gender': row.css('::attr(data-gender)').extract_first().strip(),
                'age_group': row.css('::attr(data-age)').extract_first().strip(),
                'country': row.css('::attr(data-country)').extract_first().strip(),
                'name': row.css('td:nth-child(2)::text').extract_first().strip(),
                'time_overall': row.css('td:nth-child(3)::text').extract_first().strip(),
                'time_swim': row.css('td:nth-child(4)::text').extract_first().strip(),
                'time_bike': row.css('td:nth-child(5)::text').extract_first().strip(),
                'time_run': row.css('td:nth-child(6)::text').extract_first().strip(),
                'group_rank': row.css('td:nth-child(7)::text').extract_first().strip(),
                'gender_rank': row.css('td:nth-child(8)::text').extract_first().strip(),
                'overall_rank': row.css('td:nth-child(9)::text').extract_first().strip(),
                'link': response.urljoin(detailLink),
            })

            if detailLink is not None:
                request = scrapy.Request(response.urljoin(detailLink),
                                    callback=self.parse_detail)
                request.meta['item'] = item
                yield request

    def parse_detail(self, response):
        item = response.meta['item']
        certificateString = response.css('.link-get-certificate::attr(href)').extract_first()

        item.update({
            'point': response.css('.general-info-table .swiper-slide:nth-child(4) .slide-info::text').extract_first().strip(),
            'time_T1': response.css('.transition-row .info::text')[0].extract().strip(),
            'time_T2': response.css('.transition-row .info::text')[1].extract().strip(),
            'certificate': response.urljoin(certificateString.strip()) if certificateString is not None else '',
        })

        yield item
