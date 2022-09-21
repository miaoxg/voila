import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

smtp_server = "smtp.larksuite.com"
port = 465  # For starttls
sender_addr = "miaoxiaoguang@voiladev.xyz"
password = "JjaqRIberi71YAX7"

msg = MIMEMultipart()
EMAIL_HEADER = 'IPA Admin'
email_address = 'xiao20090813xiao@163.com'
user = email_address.split('@')[0]

def format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


msg['From'] = format_addr('%s<%s>' % (EMAIL_HEADER, sender_addr))
msg['To'] = format_addr('%s' % email_address)
msg['Subject'] = Header("Password expiration reminder", 'utf-8').encode()
expried_email_text = "Hi, " + user + "\n    Your IPA password will be expried in 5 days, please change your ipa password , if you have any problem , you can find out solutions by visting the site: https://leyk1tg9lp.larksuite.com/wiki/wikusW0k1v7R5QQRF5SCK0wvq1c#"

content = MIMEText(expried_email_text, 'plain')

# Try to log in to server and send email
try:
    msg.attach(content)
    s=smtplib.SMTP_SSL(host=smtp_server, port=port)
    print("connect")
    s.login(sender_addr, password)
    print("login success")
    s.sendmail(sender_addr, email_address, msg.as_string())
    s.quit()
except Exception as e:
    # Print any error messages to stdout
    print(e)