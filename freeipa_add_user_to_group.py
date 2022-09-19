from python_freeipa import ClientMeta
import smtplib
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr

client = ClientMeta('ipa.voiladev.xyz', verify_ssl=False)
client.login('miaoxiaoguang', 'M$@qenZ4#jzwC6gx')

def add_user_to_group(email_address='', permission = ''):
    smtp_server = "smtp.larksuite.com"
    port = 465  # For starttls
    sender_addr = "miaoxiaoguang@voiladev.xyz"
    password = "JjaqRIberi71YAX7"

    msg = MIMEMultipart()
    EMAIL_HEADER = 'IPA Admin'
    user = email_address.split('@')[0]

    for i in permission:
        client.group_add_member(i, o_user=user)

    def format_addr(s):
        name, addr = parseaddr(s)
        return formataddr((Header(name, 'utf-8').encode(), addr))

    msg['From'] = format_addr('%s<%s>' % (EMAIL_HEADER, sender_addr))
    msg['To'] = format_addr('%s' % email_address)
    # msg['Cc'] = sender_addr
    msg['Subject'] = Header("Grantting Permissions Notification", 'utf-8').encode()
    email_text = "Hi, " + user + "\nYou have been granted the permission " + str(permission).strip('[|').strip('"').strip(']') + \
                ", that means you can sign in some systems with " \
                "your ipa username and password. You can find more details by visiting：" \
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
    add_user_to_group(email_address="xiao20090813xiao@163.com", permission=['operator', 'data'])