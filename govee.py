import requests, json

API_KEY = '0915aca2-be7d-4838-9197-1f4440bf7b59'
URL = 'https://developer-api.govee.com/v1/devices'

headers = {'Govee-API-Key': '{key}'.format(key = API_KEY)}
response = requests.get(URL, headers = headers).json()

print(response)