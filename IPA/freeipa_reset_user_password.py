import random
import smtplib
import string
import time
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

from python_freeipa import ClientMeta

client = ClientMeta('ipa.voiladev.xyz', verify_ssl=False)
client.login('miaoxiaoguang', 'M$@qenZ4#jzwC6gx')


def GenPassword(length):
    global user_password
    chars = string.ascii_letters + string.digits
    user_password = random.choice(string.ascii_letters) + ''.join([random.choice(chars) for i in range(length)])


def change_user_password():
    global user_password
    email_address = input('Please input your email: ')
    smtp_server = "smtp.larksuite.com"
    port = 465  # For starttls
    sender_addr = "miaoxiaoguang@voiladev.xyz"
    password = "JjaqRIberi71YAX7"

    msg = MIMEMultipart()
    EMAIL_HEADER = 'IPA Admin'
    user = email_address.split('@')[0]

    # 初始化用户密码
    client.user_mod(user, o_userpassword='vGSd833xc2vyJWkh')

    time.sleep(1)

    # 通过初始化密码，给新密码
    client.change_password(user, user_password, 'vGSd833xc2vyJWkh')

    def format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    msg['From'] = format_addr('%s<%s>' % (EMAIL_HEADER, sender_addr))
    msg['To'] = format_addr('%s' % email_address)
    # msg['Cc'] = sender_addr
    msg['Subject'] = Header("Resetting IPA Password Notification", 'utf-8').encode()
    email_text = "Hi, " + user + "\nYour IPA username is: " + user + ", password is: " + user_password + \
                 "\nUsing the username and password you can login in almost all of our systems.You can find more details by visiting：" \
                 "https://leyk1tg9lp.larksuite.com/wiki/wikusr6L09hPkmr2uPBeiQSpY2e#7GbE8c "

    plain_content = MIMEText(email_text, 'plain')

    # Try to log in to server and send email
    try:
        msg.attach(plain_content)
        s = smtplib.SMTP_SSL(host=smtp_server, port=port)
        s.login(sender_addr, password)
        s.sendmail(sender_addr, email_address, msg.as_string())
        s.quit()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    GenPassword(15)
    change_user_password()
