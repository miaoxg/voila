from python_freeipa import ClientMeta

client = ClientMeta('ipa.voiladev.xyz', verify_ssl=False)
client.login('miaoxiaoguang', 'M$@qenZ4#jzwC6gx')


def user_show():
    email_address = input("输入查询用户的邮箱: ")
    user = email_address.split('@')[0]
    result = client.user_show(user).get('result')
    print("IPA用户名: ", result.get('uid')[0])
    print("权限: ", result.get('memberof_group'))
    print("mail: ", result.get('mail')[0])
    print("密码过期时间: ", result.get('krbpasswordexpiration')[0].get('__datetime__'))
    print("密码修改时间: ", result.get('krblastpwdchange')[0].get('__datetime__'))
    print("登录失败次数: ", result.get('krbloginfailedcount')[0])


if __name__ == '__main__':
    user_show()
