import logging
import re
import smtplib

import requests
from bs4 import BeautifulSoup

SEARCH_URL = 'https://www.google.com/search?q=what%27s+my+ip'
IP_REGEX = "^(?:[0-9]{1,3}.){3}[0-9]{1,3}$"
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
        search_result = requests.get(SEARCH_URL)
        if search_result.status_code == requests.codes.ok:
            html = BeautifulSoup(search_result.content, 'html.parser')
            ip_check = re.compile(IP_REGEX)
            for div in html.body.find('div', {'id': 'search'}):
                children = div.findChildren('div', recursive=True)
                for child in children:
                    if ip_check.fullmatch(child.text):
                        try:
                            with open(FILE_NAME, 'r') as file:
                                last_ip = file.readlines()
                            if not last_ip[0].strip() == child.text.strip():
                                # write out new ip, send update email
                                last_ip[0] = child.text.strip()
                                with open(FILE_NAME, 'w') as file:
                                    file.writelines(child.text.strip())

                                send_email(child.text.strip())
                                logging.info(f'New IP is {child.text.strip()}')
                            else:
                                logging.info('IP has not changed.')
                        except FileNotFoundError:
                            # no last ip, must be first run, write to file, send email
                            file = open(FILE_NAME, 'w+')
                            file.write(child.text.strip())

                            send_email(child.text.strip())
                            logging.info(f'New IP is {child.text.strip()}')
                        finally:
                            file.close()
        else:
            logging.info(f'Request responded with {search_result.status_code} status code')
    except requests.exceptions.RequestException as e:
        logging.info(f'Something went really wrong. {e}')


if __name__ == '__main__':
    main()
