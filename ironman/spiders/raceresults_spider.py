import scrapy
from ironman.items import RaceResultItem
import urlparse
import json

class RaceResultsSpider(scrapy.Spider):
    name = "raceresults"
    fields_to_export = ['bib', 'name', 'gender', 'country', 'age_group', 'point', 'overall_rank', 'group_rank', 'gender_rank', 'time_overall', 'time_swim', 'time_bike', 'time_run', 'time_T1', 'time_T2', 'link', 'certificate']

    def __init__(self, category=None, *args, **kwargs):
        super(RaceResultsSpider, self).__init__(*args, **kwargs)
        self.logger.info('init spider')
        self.csv_filename = getattr(self, 'filename', None) or 'race_results'
        self.url = getattr(self, 'url', None)
        emailsString = getattr(self, 'emails', None) or ''
        self.emails = [x.strip() for x in emailsString.split(',')]

    def start_requests(self):
        self.logger.info('start requests')
        yield scrapy.Request(url=self.url, callback=self.parseRaceAlias)

    def parseRaceAlias(self, response):
        alias = response.css('#hdnAlias::attr(value)').extract_first()
        year = response.css('#hdnYear::attr(value)').extract_first()
        jsonPath = '../../../../../Handlers/EventLiveResultsMobile.aspx?year=' + year + '&race=' + alias
        self.logger.info('construct JSON path: ' + jsonPath)
        request = scrapy.Request(response.urljoin(jsonPath),
                            callback=self.parseJSON)
        request.meta['raceAlias'] = alias
        request.meta['jsonUrl'] = response.urljoin(jsonPath)
        yield request

    def parseJSON(self, response):
        jsonResponse = json.loads(response.body_as_unicode())
        totalPage = jsonResponse['lastPage']

        for i in range(1, totalPage + 1):
            pageUrl = response.meta['jsonUrl'] + '&p=' + str(i)
            request = scrapy.Request(pageUrl, callback=self.parsePage)
            self.logger.info('parse page ' + pageUrl)
            yield request

    def parsePage(self, response):
        jsonResponse = json.loads(response.body_as_unicode())
        raceDate = jsonResponse['raceDate']
        # count = 0
        for record in jsonResponse['records']:
            detailLink = '?bidid=' + str(record['Bib']) + '&rd=' + raceDate

            timeOverAll = record['Time']

            if timeOverAll == '--:--:--':
                timeOverAll = record['Status']
            # if count == 10:
            #     break
            # count += 1
            item = RaceResultItem({
                'bib': record['Bib'],
                'gender': record['Gender'],
                'age_group': record['AgeGroup'],
                'country': record['Country'],
                'name': record['Name'],
                'time_overall': timeOverAll,
                'time_swim': record['SwimTime'],
                'time_bike': record['BikeTime'],
                'time_run': record['RunTime'],
                'group_rank': record['AgeRank'],
                'gender_rank': record['GenderRank'],
                'overall_rank': record['OverallRank'],
                'link': response.urljoin(detailLink),
            })

            if detailLink is not None:
                request = scrapy.Request(urlparse.urljoin(self.url, detailLink),
                                    callback=self.parse_detail)
                request.meta['item'] = item
                yield request

    def parse(self, response):
        self.logger.info('parse' + str(response.headers))
        # count = 0
        for row in response.css('.content-table .race-list tbody tr'):
            self.logger.info('parse' + str(row))
            detailLink = row.css('::attr(data-result-page)').extract_first()
            timeOverAll = row.css('td:nth-child(3)::text').extract_first().strip()
            # if count == 10:
            #     break
            # count += 1
            item = RaceResultItem({
                'bib': row.css('::attr(data-bib-number)').extract_first().strip(),
                'gender': row.css('::attr(data-gender)').extract_first().strip(),
                'age_group': row.css('::attr(data-age)').extract_first().strip(),
                'country': row.css('::attr(data-country)').extract_first().strip(),
                'name': row.css('td:nth-child(2)::text').extract_first().strip(),
                'time_overall': timeOverAll,
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
            'gender': response.css('.general-info-table .swiper-slide:nth-child(2) .slide-info::text').extract_first().strip()[0],
            'point': response.css('.general-info-table .swiper-slide:nth-child(4) .slide-info::text').extract_first().strip(),
            'time_T1': response.css('.transition-row .info::text')[0].extract().strip(),
            'time_T2': response.css('.transition-row .info::text')[1].extract().strip(),
            'certificate': response.urljoin(certificateString.strip()) if certificateString is not None else '',
        })

        yield item
