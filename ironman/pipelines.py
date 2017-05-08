# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from oauth2client.service_account import ServiceAccountCredentials
from scrapy import signals
from scrapy.exporters import CsvItemExporter
from googleapiclient.discovery import build
import httplib2
import apiclient.http
import datetime
import ironman
from os.path import join, dirname

GoogleAPISecret = join(dirname(ironman.__file__), "resources", "GoogleAPISecret.json")

def callback(request_id, response, exception):
    if exception:
        # Handle error
        print exception
    else:
        print "Permission Id: %s" % response.get('id')

class CSVPipeline(object):

  def __init__(self):
    self.files = {}

  @classmethod
  def from_crawler(cls, crawler):
    pipeline = cls()
    crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
    crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
    return pipeline

  def spider_opened(self, spider):
    file = open('%s_items.csv' % spider.csv_filename, 'w+b')
    self.files[spider] = file
    self.exporter = CsvItemExporter(file)
    self.exporter.fields_to_export = spider.fields_to_export

    self.exporter.start_exporting()

    scopes = ['https://www.googleapis.com/auth/drive']
    self.credentials = ServiceAccountCredentials.from_json_keyfile_name(GoogleAPISecret, scopes)

    # Create an authorized Drive API client.
    http = httplib2.Http()
    self.credentials.authorize(http)
    self.drive_service = apiclient.discovery.build('drive', 'v3', http=http)

  def spider_closed(self, spider):
    self.exporter.finish_exporting()
    file = self.files.pop(spider)
    file.close()
    self.upload_file(spider.csv_filename, spider.url, spider.emails)

  def process_item(self, item, spider):
    self.exporter.export_item(item)
    return item

  def upload_file(self, filename, url, emails):
    # Insert a file. Files are comprised of contents and metadata.
    # MediaFileUpload abstracts uploading file contents from a file on disk.
    media_body = apiclient.http.MediaFileUpload(
        '%s_items.csv' % filename,
        mimetype = 'text/csv',
        resumable=True
    )

    today = datetime.date.today()
    # The body contains the metadata for the file.
    body = {
      'name' : filename + '_' + str(today) + '.csv',
      'title': filename + '_' + str(today) + '.csv',
      'description': 'Race ' + str(url),
    }

    # Perform the request and print the result.
    new_file = self.drive_service.files().create(body=body,
                                                 media_body=media_body).execute()
    print 'Uploaded file to google drive'
    self.share_file(new_file['id'], emails)
    return

  def share_file(self, fileId, emails):
    batch = self.drive_service.new_batch_http_request(callback=callback)

    for email in emails or []:
        user_permission = {
            'type': 'user',
            'role': 'reader',
            'emailAddress': email
        }
        batch.add(self.drive_service.permissions().create(
            fileId=fileId,
            body=user_permission,
            fields='id',
        ))

    domain_permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': 'horseuvn@gmail.com'
    }
    batch.add(self.drive_service.permissions().create(
        fileId=fileId,
        body=domain_permission,
        fields='id',
    ))
    batch.execute()
    print('Shared file to emails ' + str(emails))
    return
