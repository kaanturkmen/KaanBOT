import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from Settings import *


def send_email(username, email):
    """
    A function that takes parameter of username and email. Sending email to the user with using their
    discord nickname and given email. Sending a random integer number between [100000, 999999].
    """

    # Setting username.
    user_name = username

    # Setting email bot's email address and password.
    gmail_user = EMAIL_ADDRESS
    gmail_password = EMAIL_PASSWORD

    # Creating a random integer.
    random_int = random.randint(100000, 999999)

    # Creating required information for sending an email.
    sent_from = 'CS Türkiye'
    to = [email]

    msg = MIMEMultipart("alternative")
    msg["Subject"] = u'CS Türkiye Discord | Üniversite Başvuru Onaylama'
    msg["From"] = 'CS Türkiye'
    msg["To"] = email
    body = u"""
Merhaba %s,
Ben KaanBOT, CS Türkiye Discord sunucusunda moderasyonu sağlamakla görevliyim. Kısa bir süre önce bir kullanıcı bu mail adresini kullanarak sunucuda kendisini onaylatmaya çalıştı. Onaylanmayı sen talep etmediysen bu maili görmezden gelebilirsin. Eğer bu işlemi sen gerçekleştirdiysen alt tarafta bulunan komutu universite-rolu-basvurusu odasına yazabilirsin.

.onayla %s

Not: Bu isteği bir moderatör yardımı ile gerçekleştirdiyseniz bu kodu ona söylemeniz yeterlidir.

İyi eğlenceler!
CS Türkiye Yönetimi
    """ % (user_name, random_int)

    part1 = MIMEText(body, "plain", "utf-8")
    msg.attach(part1)
    text = msg.as_string().encode('ascii')

    # Checking if something went wrong.
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(sent_from, to, text)
        server.close()
    except Exception as e:
        print(f'Email script has an error. {e}')
        return None
    else:
        return random_int
