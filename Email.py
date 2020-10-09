import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from Settings import *


def send_email(username, email):
    user_name = username

    gmail_user = EMAIL_ADDRESS
    gmail_password = EMAIL_PASSWORD

    random_int = random.randint(100000, 999999)

    sent_from = 'CS Türkiye'
    to = [email]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = u'CS Türkiye Discord | Üniversite Başvuru Onaylama'
    msg["From"] = 'CS Türkiye'
    msg["To"] = email
    body = u"""
    Merhaba %s,
    Ben KaanBOT, CS Türkiye Discord sunucusunda moderasyonu sağlamakla görevliyim.
    Kısa bir süre önce bir kullanıcı bu mail adresini kullanarak sunucuda kendisini onaylatmaya
    çalıştı. Onaylanmayı sen talep etmediysen bu maili görmezden gelebilirsin. Eğer bu işlemi sen
    gerçekleştirdiysen alt tarafta bulunan komutu universite-rolu-basvurusu odasına yazabilirsin.

    .onayla %s

    İyi eğlenceler!
    """ % (user_name, random_int)

    part1 = MIMEText(body, "plain", "utf-8")
    msg.attach(part1)
    text = msg.as_string().encode('ascii')

    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, text)
        server.close()
    except:
        print('Email script has an error.')
        return None
    else:
        return random_int
