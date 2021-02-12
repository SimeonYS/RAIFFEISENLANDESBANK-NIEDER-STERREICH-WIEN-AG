import scrapy
import re
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst
from ..items import NoewItem

pattern = r'(\r)?(\n)?(\t)?(\xa0)?'
# date = re.findall(r'\d+\.\s\w+\s\d+',article, re.UNICODE) -- don`t mind me, testing regex

class SpiderSpider(scrapy.Spider):
    name = 'spider'

    start_urls = ['https://www.raiffeisen.at/noew/rlb/de/meine-bank/presse/presseaussendungen.html',
                  'https://www.raiffeisen.at/noew/rlb/de/meine-bank/presse/nachlese.html'
                  ]

    def parse(self, response):
        articles = response.xpath('//div[@class="content-row aem-GridColumn aem-GridColumn--default--1"]/section[@class="component-pictureText content-section component-spacer "]')
        for article in articles:
            date = article.xpath('.//p[1]/text()').get()
            links = article.xpath('.//div[@class="cta-wrapper"]//a/@href').get()
            url = response.urljoin(links)
            yield response.follow(url, self.parse_article,cb_kwargs=dict(date = date))

    def parse_article(self, response, date):
        item = ItemLoader(NoewItem())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//section[@class="component-page-title component-spacer"]//text()').getall()
        title = re.sub(pattern, "", ''.join(title).strip())
        content = response.xpath('//div[@class="component-text rte "]//text()|//div[@class="text-wrapper rte"]//text()|//div[@class="component-content-box-teaser "]//text()').getall()
        content = [text.strip() for text in content if text.strip()]
        content = re.sub(pattern, "", ' '.join(content))

        item.add_value('date', date)
        item.add_value('title', title)
        item.add_value('link', response.url)
        item.add_value('content', content)
        return item.load_item()