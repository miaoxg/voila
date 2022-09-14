from python_freeipa import ClientMeta
import smtplib, ssl
import time
client = ClientMeta('ipa.voiladev.xyz', verify_ssl=False)
client.login('miaoxiaoguang', 'M$@qenZ4#jzwC6gx')
# user = client.user_add('test3', 'John', 'Doe', 'John Doe', o_preferredlanguage='EN')
result_list = client.user_find(o_sizelimit=200).get('result')
i = 0
while i < len(result_list):
    # if  result_list[i].get('uid') != ['admin'] or result_list[i].get('nsaccountlock') == True :
    if  result_list[i].get('nsaccountlock') == True:
        # print(result_list[i].get('uid'), " is locked!")
        pass
    elif result_list[i].get('krbpasswordexpiration') is None:
        # print(result_list[i].get('uid'), "密码永不过期")
        pass
    elif result_list[i].get('krbpasswordexpiration')[0].get('__datetime__') :

        print(result_list[i].get('uid')[0], result_list[i].get('mail')[0], result_list[i].get('krbpasswordexpiration')[0].get('__datetime__'))
    i += 1
    time.sleep(0.2)
