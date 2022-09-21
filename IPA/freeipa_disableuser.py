from python_freeipa import ClientMeta

client = ClientMeta('ipa.voiladev.xyz', verify_ssl=False)
client.login('miaoxiaoguang', 'M$@qenZ4#jzwC6gx')
user = input('Please input a username: ')
client.user_disable(user)
