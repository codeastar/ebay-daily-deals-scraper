import csv
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class EBayBDPipeline(object):

    def open_spider(self, spider):
        self.file = csv.writer(open(spider.file_name, 'w', newline='', encoding = 'utf8') )
        fieldnames = ['Item_name', 'Category', 'Link', 'Image_path', 'Curreny', 'Price', 'Original_price']
        self.file.writerow(fieldnames)
      
#    def close_spider(self, spider):
#        self.file.close()

    def process_item(self, item, spider):

        self.file.writerow([item['name'], item['category'],item['link'], 
                    item['img_path'] , item['currency'],item['price'], 
                    item['orignal_price']])

        return item