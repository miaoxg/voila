from python_freeipa import ClientMeta
import time
from datetime import datetime
import smtplib, ssl
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

client = ClientMeta('ipa.voiladev.xyz', verify_ssl=False)
client.login('miaoxiaoguang', 'M$@qenZ4#jzwC6gx')
result_list = client.user_find(o_sizelimit=200).get('result')
now = int(datetime.now().strftime('%Y%m%d%H%M%S'))
user = client.user_add('test3', 'John', 'Doe', 'John Doe', o_preferredlanguage='EN')

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
    # expried_email_text = "Hi, " + user + "\nYour IPA password will be expried in 7 days or has already expried, please change your ipa password , if you have any problem , you can find out drictions by visting the site: https://leyk1tg9lp.larksuite.com/wiki/wikusW0k1v7R5QQRF5SCK0wvq1c#"
    expried_email_html = """\
    <html>
        <head></head>
        <body>
            <p>Hi,
                <br>Your IPA password will be expried in 7 days or has already expried, please change your ipa password .
                    If you have any problem , you can find out drictions by visting the site below: <br>
                    <a href="https://leyk1tg9lp.larksuite.com/wiki/wikusW0k1v7R5QQRF5SCK0wvq1c#J9RqGM">Click here</a>
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