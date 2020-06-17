import logging
import json

import requests

IPIFY_PUB_IP_URL = 'https://api6.ipify.org?format=json'
GOOGLE_DYNAMIC_DNS_UPDATE = 'https://{}:{}@domains.google.com/nic/update?hostname={}&myip={}'
FILE_NAME = 'ip.txt'
DOMAIN = '<DOMAIN_NAME>'
USER_NAME = '<DDNS_USER>'
PASSWORD = '<DDNS_PASSWORD>'


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
                    # write out new ip, update dns record
                    with open(FILE_NAME, 'w') as file:
                        file.writelines(ip_address)

                    logging.info(f'New IP is {ip_address}')

                    dns_update = requests.post(
                        GOOGLE_DYNAMIC_DNS_UPDATE.format(USER_NAME, PASSWORD, DOMAIN, ip_address)
                    )
                    dns_update_result = dns_update.text
                    if dns_update_result.find('good') != 0:
                        logging.info('Google DNS update was successful.')
                    else:
                        logging.error(f'Google DNS update was unsuccessful or updated in error {dns_update.text}')
                else:
                    logging.info('IP has not changed.')
            except FileNotFoundError:
                # no last ip, must be first run, write to file, update dns record
                with open(FILE_NAME, 'w+') as file:
                    file.write(ip_address)

                logging.info(f'New IP is {ip_address}')

                dns_update = requests.post(
                    GOOGLE_DYNAMIC_DNS_UPDATE.format(USER_NAME, PASSWORD, DOMAIN, ip_address)
                )
                dns_update_result = dns_update.text
                if dns_update_result.find('good') != 0:
                    logging.info('Google DNS update was successful.')
                else:
                    logging.error(f'Google DNS update was unsuccessful {dns_update.status_code} : {dns_update.text}')
        else:
            logging.info(f'Request responded with {search_result.status_code} status code')
    except requests.exceptions.RequestException as e:
        logging.info(f'Something went really wrong. {e}')


if __name__ == '__main__':
    main()
