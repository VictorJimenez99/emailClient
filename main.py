import smtplib, ssl
import time

import pwinput
import requests

import urllib.request


def try_connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host)  # Python 3.x
        return True
    except:
        return False


# test

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
    if not try_connect():
        time.sleep(10)
        print("Unable to connect to google servers")
        continue

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

    tagged_messages = []
    for contact in list_mails_update:
        message = "Subject: Generic Alert VICERI\n\n\n"
        for event in list_needs_update:
            ev_str = f"Event: {event.get('event')}\nCulprit: {event.get('culprit')}\nTime: {event.get('time_str')}"
            if event not in tagged_messages:
                tagged_messages.append(event)
            message += f"{ev_str}\n\n----------\n\n"

        if len(tagged_messages) >= 1:
            try:
                with smtplib.SMTP(smtp_server, port) as server:
                    server.ehlo()  # Can be omitted
                    server.starttls(context=context)
                    server.ehlo()  # Can be omitted
                    server.login(sender_email, password)
                    server.sendmail(sender_email, contact, message)

                for event in tagged_messages:
                    status = sess.post(url_get_set_send, json={"id": event.get('id')}).status_code
                    print(f"sent message to: {contact}")
                    print(f"update_status for event: {event.get('id')}: {status}")

            except Exception as e:
                continue

    print(f"sleeping for: {sleep_time}")
    time.sleep(sleep_time)
