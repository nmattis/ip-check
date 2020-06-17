import json
import logging
import smtplib

import requests

IPIFY_PUB_IP_URL = 'https://api6.ipify.org?format=json'
FILE_NAME = 'ip.txt'
OUTGOING = 'smtp.gmail.com'
PORT = 465
USER_NAME = '<gmail user>'
PASSWORD = '<gmail password>'
EMAIL_RECIPIENT = '<email recipient>'
EMAIL_MESSAGE = "Subject: New Home Public IP\nIP Address is {!s}"


def send_email(ip_address):
    server = smtplib.SMTP_SSL(OUTGOING, PORT)
    server.login(USER_NAME, PASSWORD)
    server.sendmail(USER_NAME, EMAIL_RECIPIENT, EMAIL_MESSAGE.format(ip_address))
    server.quit()


def main():
    logging.basicConfig(
        filename='ip_check.log',
        level=logging.INFO,
        format='%(asctime)s %(message)s',
        datefmt='%m/%d/%Y %I:%M:%S %p'
    )
    try:
        pub_ip_address = requests.get(IPIFY_PUB_IP_URL)
        if pub_ip_address.status_code == requests.codes.ok:
            ip_address = json.loads(pub_ip_address.text)['ip']
            try:
                with open(FILE_NAME, 'r') as file:
                    last_ip = file.readlines()
                if not last_ip[0].strip() == ip_address:
                    # write out new ip, send update email
                    with open(FILE_NAME, 'w') as file:
                        file.writelines(ip_address)

                    send_email(ip_address)
                    logging.info(f'New IP is {ip_address}')
                else:
                    logging.info('IP has not changed.')
            except FileNotFoundError:
                # no last ip, must be first run, write to file, send email
                with open(FILE_NAME, 'w+') as file:
                    file.write(ip_address)

                send_email(ip_address)
                logging.info(f'New IP is {ip_address}')
        else:
            logging.error(f'Request responded with {search_result.status_code} status code')
    except requests.exceptions.RequestException as e:
        logging.error(f'Something went really wrong. {e}')


if __name__ == '__main__':
    main()
