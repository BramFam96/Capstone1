import requests
import os
from api.secret import *

key = os.environ.get('API_KEY', LOCAL_KEY)

def config_path(slug):
  url = f'https://v1-sneakers.p.rapidapi.com/v1/{slug}'
  headers = {
    "X-RapidAPI-Host": "v1-sneakers.p.rapidapi.com",
    "X-RapidAPI-Key": f"{key}"
  }
  return (url, headers)

def get_data(url, headers, data = None):
  res = requests.request("GET", url, headers=headers, params=data)
  return res.json()
##############################################################################

############## Api Calls

# Sneakers
def get_sneakers(data = {'limit':'20'}):
  
  url, headers = config_path('sneakers')
  d = {'limit':'20'}
  if 'limit' not in data:
    d = {'limit':'20'}
    d.update(data)
  q = get_data(url, headers, d)
  shoe_list = q['results']
  
  return shoe_list

def get_sneaker_by_id(sneaker_id):
  url, headers = config_path(f'sneakers/{sneaker_id}')
  q = get_data(url, headers)
  shoe = q['results']
  return shoe

# Brands
def get_brands():
  url, headers = config_path('brands')

  q = get_data(url, headers)
  brand_list = [b.title() for b in q['results']]
  
  return brand_list
