from python_freeipa import ClientMeta
import random, string
import datetime
import smtplib, ssl
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

client = ClientMeta('ipa.voiladev.xyz', verify_ssl=False)
client.login('miaoxiaoguang', 'M$@qenZ4#jzwC6gx')

password_expiration_time = datetime.datetime.now() + datetime.timedelta(days=90)
password_expiration_time_format = password_expiration_time.strftime("%Y%m%d%H%M%SZ")
user_password = ""


def GenPassword(length):
    global user_password
    chars = string.ascii_letters + string.digits
    user_password = random.choice(string.ascii_letters) + ''.join([random.choice(chars) for i in range(length)])

def add_user(email_address='',firstname='', lastname='', fullname='', permission = ''):
    global user_password
    smtp_server = "smtp.larksuite.com"
    port = 465  # For starttls
    sender_addr = "miaoxiaoguang@voiladev.xyz"
    password = "JjaqRIberi71YAX7"

    msg = MIMEMultipart()
    EMAIL_HEADER = 'IPA Admin'
    user = email_address.split('@')[0]

    client.user_add(user, firstname, lastname, fullname, o_preferredlanguage='EN',
                    o_krbpasswordexpiration=password_expiration_time_format, o_mail=email_address,
                    o_userpassword=user_password)
    for i in permission:
        client.group_add_member(i, o_user=user)

    def format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    msg['From'] = format_addr('%s<%s>' % (EMAIL_HEADER, sender_addr))
    msg['To'] = format_addr('%s' % email_address)
    # msg['Cc'] = sender_addr
    msg['Subject'] = Header("欢迎加入Voila大家庭", 'utf-8').encode()
    email_text = "Hi, " + user + "\nYour IPA username is: " + user + ", password is: " + user_password + \
                 "\nUsing the username and password you can login in almost all of our systems." + \
                 " As a freshman in Voila, you can get a quick start by visting the site: " \
                 "https://leyk1tg9lp.larksuite.com/wiki/wikusr6L09hPkmr2uPBeiQSpY2e \n" \
                 "[Notice]: Please do not use the email: " + email_address + " to register https://creator.voila.love or " \
                 "https://creator.voiladev.xyz !!!"

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
    add_user(email_address="xiao20090813xiao@163.com", firstname='xiaoguang', lastname='miao', fullname='xiaoguangmiao', permission=['vpn', 'data'])