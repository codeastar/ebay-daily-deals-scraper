import scrapy
from scrapy.http import HtmlResponse
import json, re, datetime
from ebaybd.items import EBayItem

def formatPrice(price, currency):
    if price is None:
        return None
 
    price = price.replace(currency, "")
    price = price.replace(",", "")
    price = price.strip()
    return price

def getItemInfo(htmlResponse, category):
    eBayItem = EBayItem()
    
    name = htmlResponse.css(".ebayui-ellipsis-2::text").extract_first()
    if name is None: 
        name = htmlResponse.css(".ebayui-ellipsis-3::text").extract_first()
    link = htmlResponse.css("h3.dne-itemtile-title.ellipse-2 a::attr(href)").extract_first()
    if link is None: 
        link = htmlResponse.css("h3.dne-itemtile-title.ellipse-3 a::attr(href)").extract_first()
    eBayItem['name'] = name   
    eBayItem['category'] = category
    eBayItem['link'] = link
    eBayItem['img_path'] = htmlResponse.css("div.slashui-image-cntr img::attr(src)").extract_first()
    currency = htmlResponse.css(".dne-itemtile-price meta::attr(content)").extract_first()
    if currency is None: 
        currency =  htmlResponse.css(".dne-itemtile-original-price span::text").extract_first()[:3]
    eBayItem['currency'] = currency
    eBayItem['price'] = formatPrice(htmlResponse.css(".dne-itemtile-price span::text").extract_first(), currency)
    eBayItem['orignal_price'] = formatPrice(htmlResponse.css(".dne-itemtile-original-price span::text").extract_first(), currency)

    return eBayItem

class BDSpider(scrapy.Spider):
    name = "ebaybd"
    #use current date as file name
    file_name = datetime.datetime.now().strftime("%F") +".csv"

    def start_requests(self):
        urls = [
            'https://www.ebay.com/globaldeals'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):

        self.log("--- Handle Spotlight Deals ---")
        #spotlight deals
        spl_deal = response.css(".ebayui-dne-summary-card.card.ebayui-dne-item-featured-card--topDeals")
        spl_title = spl_deal.css("h2 span::text").extract_first()
        
        eBayItem = getItemInfo(spl_deal, spl_title)
        yield eBayItem    

        #feature deals
        self.log("--- Handle Feature Deals ---")
        feature_deal_title = response.css(".ebayui-dne-banner-text h2 span::text").extract_first()
        feature_deals_card = response.css(".ebayui-dne-item-featured-card")
        feature_deals = feature_deals_card.css(".col")
        
        for feature in feature_deals:
             eBayItem = getItemInfo(feature, feature_deal_title)
             yield eBayItem 

        self.log("--- Handle Other Categories ---")
        #card deals
        cards = response.css(".ebayui-dne-item-pattern-card.ebayui-dne-item-pattern-card-no-padding")    
        for card in cards:
            title = card.css("h2 span::text").extract_first()
            more_link = card.css(".dne-show-more-link a::attr(href)").extract_first()
            if more_link is not None:
                 cat_id = re.sub(r"^https://www.ebay.com/globaldeals/|featured/|/all$","",more_link)
                 cat_id = re.sub("/",",",cat_id)
                 self.log("Cat ID:{} ".format(cat_id))
#                 if ((title == "Tablets & Laptops" ) or (title == "Men's Fashions")):
                 cat_listing = "https://www.ebay.com/globaldeals/spoke/ajax/listings?_ofs=0&category_path_seo={}&deal_type=featured".format(cat_id)
#                  self.log(cat_listing)

                 request = scrapy.Request(cat_listing, callback=self.parse_cat_listing)
                 request.meta['category'] = title
                 request.meta['page_index'] = 1
                 request.meta['cat_id'] = cat_id
                 yield request
            else:
                 self.log("Get item on page for {}".format(title))
                 category_deals = card.css(".item")
                 for c_item in category_deals:
                    eBayItem = getItemInfo(c_item, title)
                    yield eBayItem
                                      
    def parse_cat_listing(self, response):
        category = response.meta['category']
        page_index = response.meta['page_index']
        cat_id = response.meta['cat_id']

        data = json.loads(response.body)
        fulfillment_value =  data.get('fulfillmentValue')
        listing_html = fulfillment_value['listingsHtml']
        is_last_page = fulfillment_value['pagination']['isLastPage']
        json_response = HtmlResponse(url="json response", body=listing_html, encoding='utf-8')
        items_on_cat = json_response.css(".col")
        str_item_size = str(len(items_on_cat))
        
        for item in items_on_cat:
              eBayItem = getItemInfo(item, category)
              yield eBayItem

        self.log("--- Items on a category: ["+category+"] --- size: "+str_item_size)
        self.log("Is last page: {}".format(is_last_page))

        #do next page
        if (is_last_page == False): 
            item_starting_index = page_index * 24
            cat_listing = "https://www.ebay.com/globaldeals/spoke/ajax/listings?_ofs={}&category_path_seo={}&deal_type=featured".format(item_starting_index, cat_id)
            request = scrapy.Request(cat_listing, callback=self.parse_cat_listing)
            request.meta['category'] = category
            request.meta['page_index'] = page_index+1
            request.meta['cat_id'] = cat_id
            yield request     
