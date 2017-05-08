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

GoogleAPISecret = {
  "type": "service_account",
  "project_id": "ironman-scrapy",
  "private_key_id": "e1f820d0e65ca25b5ef512ce09e02453ef1c6e6d",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDStcXgpPZL3Crc\nyIaCzG3xFuu36f8uG9VvMVVG1Uknd0ADp+jYAnvGzuiRNtZxP8SH7unjmTo0DSfZ\niV3PPosUkI6J+7KSA1uB4dVqFKDouI75Kfb6TWJoMgBDRyg9maRZNH9HECWEWYbi\ng9Yb+YSaraG/G4TNOli1Bmum1Z3AeMtpmWoE+zeVzb4IWux938N6yo6llAH65DS+\nk2GhUnMDSzijIjnatooRR5ZcMYkG3Y/hfFpsiwwB8S2oVxMZtsVbjor1qhETYAyA\nioqKDl0ke3ZHlkrXLsaBmAATGFiGXKAlGqR5uEurq6KPXYCq95UGefU9QH9SpuDc\nultfLm3DAgMBAAECggEASikD3g7xSL3SsCY7gWmmAEaK7A4FbBsLwbjhRK7osmU8\nOI0uXGhzXAOSwxlD3FQPPbCOzTYu0AcZUW0RgVGH7dL6+AGIVe+sk0gCrvVXtNDQ\nMU3dyTbXPcjrYsJ2nUeoGmVprn82VSCVYr/36ZymWTJnTTXIRdsVQZFi7jMc9JJr\nt5xGGKqjosTSTvdhRIy6M8ckBtPAdoCsBshIyyMenlKpc+m60b9LOVUwZxwMLIxO\n7ESmmrCjShw9TOr2zfDjjyPyDGEbNVrAGQOniSMo+Y3/vUdRiRbjMMT+OpQObf50\nG4CGxBd4Rtav38FJ8N96/zX/j8kNVVn+cy85wma5AQKBgQDpywZ2diAmk3MIktHs\nAgGDUuOKU176w0Ks08DwYYN6yh4x/IK5oinGCBH6u/dbmQA0FL7sg+aqpRptWudy\npap8IhcI8PM06zLeO4kpZaL7bSVSAUQ17hL0QgZ/vOQbxb77hRprfSpm2JtgUtT1\nYNhBva9CBEtbYABJr58xJumoAwKBgQDmuXR0qyYiSQC7Uk/ME73EjnA98gHOFDbB\ns9u/aXOKzCa/Jbuu4pnlTXYMmy750Gou7tE94aLfAzY//W869THOB6PBf6x/nJ+R\noHA0Lye5NaCqWofP33K+B86ZW5KWGHCxUoDlil6QvPd04rBCGom9chykuupLuIBp\n4YGSe+uXQQKBgCYvUs7mXDnwu0kbMc4qRbT9RMzC8TBj0/AGZezdAGx9tpDTfUZ0\nhf4iM02QhcYgJzhaaxSWNoaIkNhrkIHZLQ85QinjsNVj1NsXPj/UqdoG6aGLM2jb\niZz7a7RRVbBzi83o33fO6a4Ckt4YqU+qkaerI4TUzroN4/4lAQs2H9OhAoGASrOz\nC+86CpG+ZegRpA6kO5auqq/He9S5od+8/22CFmdhCDSMXuRJVZ/N3+kCvamIJ6f1\nIWcD19bvYqqIr/shZAa/M3BGBo9MbtcWXR8Daoj9ewqSvHApc3ONpcOrY2OIYTFI\nQImbcptsN3EKBm0XObpPodpO77NOCHoV/LqYncECgYBAtSwehKtZP/y7RYIhUXr2\njMxF9dJYYKD90L2KV8CzIMZYYXhqWNDD9r/M+OU5zxalFHMHpDrq2vweyiuGmNj4\ncfXqOx4vKOcCWkes6RUjw6ftYTAjyog89vuIxLkjzfI4ra2PsISQUM5++mp6QM6a\neSJ/G8T6Gb/gbbpOIYBfsw==\n-----END PRIVATE KEY-----\n",
  "client_email": "admin-612@ironman-scrapy.iam.gserviceaccount.com",
  "client_id": "107767311000103791322",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/admin-612%40ironman-scrapy.iam.gserviceaccount.com"
}

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
    self.credentials = ServiceAccountCredentials.from_json_keyfile_dict(GoogleAPISecret, scopes)

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
