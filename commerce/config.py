import os
import json

with open('/etc/commerce_config.json') as config_file:
    config = json.load(config_file)

class Config:
    DJANGO_KEY  = config.get('django_key')
