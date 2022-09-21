#!/usr/bin/python3
import urllib

import httplib2

url = 'https://oauth.voila.love/auth'
body = {'username': 'xiao20090813xiao@163.com',
        'password': 'hpart8XJ0xSAY6BBXIWhBigDsjMypIDtPD9pREadWzocK++t1HhCM+GrDcRqgwp+ZpF4CpHY8j7oHuQWP3idNAnxSph9DuCr3akkeIYryQRPsT1QgmehGFjIfnJYWT5ehpgHlT7jts0XH/fGqw94+QcbIPg+b9IJDwwSJMMVcvE='}
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json'
}

http = httplib2.Http()
response, content = http.request(url, 'POST', headers=headers, body=urllib.parse.urlencode(body))
print(response)
# headers = {'Cookie': response['set-cookie'],
#     "query":"red"
# }
#
# url = 'https://creator.voila.love/bio/'
# response, content = http.request(url, 'POST', headers=headers)
# print(response,content)


# headers['Cookie'] = response['set-cookie']
