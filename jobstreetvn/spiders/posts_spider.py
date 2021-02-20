import scrapy
import json

class PostsSpider(scrapy.Spider):
    name = "posts"

    start_urls = {
        "https://www.jobstreet.vn/j?sp=search&q=C%C3%B4ng+ngh%E1%BB%87+th%C3%B4ng+tin&l"
    }
    
    #NON ADS
    def parse_item(self, response):
        item = {}
        company_name1 = response.css("#company-location-container > span.company::text").get()
        company_name2 = response.xpath("//*[@id='job-description-container']/div/div/p[17]/b/text()").get()
        company_name3 = response.css("#job-description-container > div > div > strong ::text").get()
        company_ads = response.css(".job-title::text").get()
        if company_name1:
            #no ads
            #top
            item["type"] = "no ads",
            item["jobtitle"] = response.css("h3.job-title.heading-xxlarge ::text").get(),
            item["company_name"] = company_name1,
            item["location"] = response.css("#company-location-container > span.location ::text").get(),
            item["site"] = response.css("#job-meta > span.site ::text").get(),
            #desc
            item["desc"] = ''.join(response.css("#job-description-container ::text").getall()),
        elif company_name2:#company di bawah
            #no ads
            #top
            item["type"] = "no ads, company name at the bottom side",
            item["jobtitle"] = response.css("h3.job-title.heading-xxlarge ::text").get(),
            item["company_name"] = response.xpath("//*[@id='job-description-container']/div/div/p[17]/b/text()").get(),
            item["location"] = response.css("div #company-location-container > span.location ::text").get(),
            item["site"] = response.css("div #job-meta > span.site ::text").get(),
            #desc
            item["desc"] = ''.join(response.css("#job-description-container ::text").getall())
        else: #no description
            item["type"] = "no ads, no desc",
            item["jobtitle"] = response.css("h3.job-title.heading-xxlarge ::text").get(),
            item["company_name"] = company_name3
            item["location"] = response.css("#company-location-container > span.location ::text").get(),
            item["site"] = response.css("#job-meta > span.site ::text").get(),
            item["desc"] = "no desc"
        return item 
    
    #ADS
    def parse_item_ads(self, response):
        item={}
        company_ads = response.css(".job-title::text").get()
        if company_ads:
            item["type"] = "ads"
            item["jobtitle"] = response.css(".job-title::text").get()
            item["company_name"] = company_ads
            item["location"] = response.css(".location::text").get()
            item["site"] = response.css(".site::text").get()
            item["desc"] = ''.join(response.css("#job-description-container ::text").getall())
        return item

    def parse_item_json(self, response):
        text_clean = response.text.replace("/**/_jsonp_0(", "")
        text_clean = text_clean.replace(")", "")
        result_json = json.loads(text_clean)
        for data in result_json['ads']:
            url = data['url']
            yield scrapy.Request(url = url, callback = self.parse_item_ads)
          
    def parse(self, response):
        page_number = 1
        for post in response.css('a.job-item'):
            data = {
                #total = 15, ads = 5, non ads = 10
                #non ads
                "url" : post.css(".job-item ::attr(href)").get()
            }
            linkads = f"https://jupiter.jora.com/api/v1/jobs?keywords=C%C3%B4ng%20ngh%E1%BB%87%20th%C3%B4ng%20tin&page_num={page_number}&session_id=1f4498b9c6f2ebda3cd5dcdf8ef6b15f&search_id=3yAkpixVHSHokFUnNESz-1f4498b9c6f2ebda3cd5dcdf8ef6b15f-X86gxLy3TuLx42PSU59a&session_type=web&user_id=3yAkpixVHSHokFUnNESz&logged_user=false&mobile=false&site_id=1&country=VN&host=https://jupiter.jora.com&full_text_only_search=true&ads_per_page=5&callback=_jsonp_0"
            link = "https://www.jobstreet.vn/" + data.get("url")
            page_number +=1
            if link is not None:
                yield scrapy.Request(url = link, callback = self.parse_item)
            yield scrapy.Request(url = linkads, callback = self.parse_item_json)

        next_page = response.css("a.next-page-button::attr(href)").get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
        yield scrapy.Request(next_page, callback=self.parse)
        