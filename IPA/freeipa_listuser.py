from datetime import datetime

from python_freeipa import ClientMeta

client = ClientMeta('ipa.voiladev.xyz', verify_ssl=False)
client.login('miaoxiaoguang', 'M$@qenZ4#jzwC6gx')
result_list = client.user_find(o_sizelimit=200).get('result')
now = int(datetime.now().strftime('%Y%m%d%H%M%S'))

i = 0
while i < len(result_list):
    if result_list[i].get('nsaccountlock') == True:
        pass
        # print(result_list[i].get('uid')[0], " 被disabled!")
    elif result_list[i].get('krbpasswordexpiration') is None:
        pass
        # print(result_list[i].get('uid')[0], "密码永不过期")
    elif result_list[i].get("krbloginfailedcount") is not None:
        print(result_list[i].get('uid')[0], result_list[i].get('mail')[0], "密码输入错误次数：",
              result_list[i].get("krbloginfailedcount")[0])
    elif int(result_list[i].get('krbpasswordexpiration')[0].get('__datetime__').split('Z')[0]) - now < 7 * 1000000:
        print(result_list[i].get('uid')[0], result_list[i].get('mail')[0], "密码即将到期",
              result_list[i].get('krbpasswordexpiration')[0].get('__datetime__'))
    else:
        pass
    i += 1
