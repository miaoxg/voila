import smtplib
import time
from datetime import datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

from python_freeipa import ClientMeta

client = ClientMeta('ipa.voiladev.xyz', verify_ssl=False)
client.login('miaoxiaoguang', 'M$@qenZ4#jzwC6gx')
result_list = client.user_find(o_sizelimit=500).get('result')
now = int(datetime.now().strftime('%Y%m%d%H%M%S'))

print("result_list is", result_list)


def send_email(email_address=''):
    smtp_server = "smtp.larksuite.com"
    port = 465  # For starttls
    sender_addr = "miaoxiaoguang@voiladev.xyz"
    password = "JjaqRIberi71YAX7"

    msg = MIMEMultipart()
    EMAIL_HEADER = 'IPA Admin'
    # email_address = ''
    user = email_address.split('@')[0]

    def format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    msg['From'] = format_addr('%s<%s>' % (EMAIL_HEADER, sender_addr))
    msg['To'] = format_addr('%s' % email_address)
    # msg['Cc'] = sender_addr
    msg['Subject'] = Header("Password expiration remind", 'utf-8').encode()
    # expried_email_text = "Hi, " + user + "\nYour IPA password will  expried in 7 days or has already expried, please change your ipa password , if you have any problem , you can find out drictions by visting the site: https://leyk1tg9lp.larksuite.com/wiki/wikusW0k1v7R5QQRF5SCK0wvq1c#"
    expried_email_html = """\
    <html>
        <head></head>
        <body>
            <p>Hi,
                <br>Your IPA password will expire within 7 days or has already expired, 
                that means you can't login to almost all of voila systems,such as https://dashboard.voila.love, https://git.voiladev.xyz and so on.
                Please reset your IPA password.If you have any problem, you can find out drictions by visting the site below: <br>
                <a href="https://leyk1tg9lp.larksuite.com/wiki/wikusW0k1v7R5QQRF5SCK0wvq1c#J9RqGM">内网平台密码及登录问题排查流程</a>
            </p>
        </body>
    </html>
    """

    # plain_content = MIMEText(expried_email_text, 'plain')
    html_content = MIMEText(expried_email_html, 'html')

    # Try to log in to server and send email
    try:
        # msg.attach(plain_content)
        msg.attach(html_content)
        s = smtplib.SMTP_SSL(host=smtp_server, port=port)
        s.login(sender_addr, password)
        s.sendmail(sender_addr, email_address, msg.as_string())
        s.quit()
    except Exception as e:
        print(e)


i = 0
while i < len(result_list):
    print("result_list[i] is :", result_list[i])
    if result_list[i].get('nsaccountlock') == True:
        print(result_list[i].get('uid'), " is locked!")
    elif result_list[i].get('krbpasswordexpiration') is None:
        print(result_list[i].get('uid'), "密码永不过期")
    elif int(result_list[i].get('krbpasswordexpiration')[0].get('__datetime__').split('Z')[0]) - now > 7 * 1000000:
        print(result_list[i].get('uid'), "密码正常", result_list[i].get('krbpasswordexpiration')[0].get('__datetime__'))
    else:
        send_email(result_list[i].get('mail')[0])
        print("Your passport will expried in 7 days : ", result_list[i].get('uid')[0], result_list[i].get('mail')[0],
              result_list[i].get('krbpasswordexpiration')[0].get('__datetime__'))
    i += 1
    time.sleep(0.2)
