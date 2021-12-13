import smtplib, ssl
import time

import pwinput
import requests

smtp_server = "smtp.gmail.com"
port = 587  # For starttls
sender_email = "viceri.redes3@gmail.com"
password = pwinput.pwinput(mask='*')
password = password.strip()

context = ssl.create_default_context()

server_url = "http://localhost:5000/"
url_get_not_sent = "http://localhost:5000/log_get_not_sent"
url_get_set_send = "http://localhost:5000/log/set_sent_status"
url_get_mail = "http://localhost:5000/log_get_mails"

while True:

    sess = requests.Session()
    credentials_json = {"name": "root", "password": "root"}
    # payload_req = {'json_payload': credentials_json}
    login_request = sess.post(f"{server_url}create_session",
                              json=credentials_json)
    print(f"update: request: {login_request}")

    response_ss = sess.get(url_get_not_sent)
    if response_ss.status_code != 200:
        print("messagw: error sleeping for 10s")
        time.sleep(10)
        continue
    json_ret = response_ss.json()
    list_needs_update = json_ret.get("values")
    sleep_time = int(json_ret.get("sleep_time"))
    print(list_needs_update)

    list_mails_response = sess.get(url_get_mail)
    if list_mails_response.status_code != 200:
        print("mail error sleeping for 10s")
        time.sleep(10)
        continue
    json_ret_mail = list_mails_response.json()
    list_mails_update = json_ret_mail.get("emails")

    for mail in list_needs_update:
        for contact in list_mails_update:
            with smtplib.SMTP(smtp_server, port) as server:
                server.ehlo()  # Can be omitted
                server.starttls(context=context)
                server.ehlo()  # Can be omitted
                server.login(sender_email, password)
                server.sendmail(sender_email,
                                contact,
                                f"Subject: Alerta Generica VICERI\n\n\nEvent: {mail.get('event')}\nCulprit: {mail.get('culprit')}\nTime: {mail.get('time_str')}")
                status = sess.post(url_get_set_send, json={"id": mail.get('id')}).status_code
                print(f"sent message to: {contact}")
                print(f"update_status for event: {mail.get('id')}: {status}")

    print(f"sleeping for: {sleep_time}")
    time.sleep(sleep_time)
