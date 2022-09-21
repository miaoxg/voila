from python_freeipa import ClientMeta

client = ClientMeta('ipa.voiladev.xyz', verify_ssl=False)
client.login('miaoxiaoguang', 'M$@qenZ4#jzwC6gx')


def user_unlock():
    email_address = input("输入待解锁的邮箱: ")
    user = email_address.split('@')[0]
    client.user_unlock(user)


if __name__ == '__main__':
    user_unlock()
