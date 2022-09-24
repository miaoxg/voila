import json
import logging
import time

import requests
from pushgateway_client import client

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(filename)s %(funcName)s：line %(lineno)d threadid %(thread)d %(levelname)s %(message)s",
                    datefmt='%Y-%m-%d %H:%M:%S'
                    )


def pushalert(metric_name="test", metric_value="-1", job_name="job_name"):
    result = client.push_data(
        url="pushgateway.voiladev.xyz:32684",
        metric_name=metric_name,
        metric_value=metric_value,
        job_name=job_name,
        timeout=5,
        labels={
            "env": "prod"
        }
    )


def useboncer_check():
    while True:
        url = "https://api.usebouncer.com/v1/customer/user/current/credit"

        header = {
            'authority': 'api.usebouncer.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;'
                      'q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'en,zh;q=0.9,zh-CN;q=0.8',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            "sec-ch-ua-platform": "macOS",
            'sec-fetch-dest': 'document',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'x-api-key': '11rVwtTjIoCOk9wxXd9sPyMsqpUGRCWVhGSKZm8S'
        }

        response = requests.get(url, headers=header)

        available_email_num = json.loads(response.text).get('credits')

        logging.info('response.status_code is %s, available_email_num is %s', response.status_code, available_email_num)

        pushalert("usebouncer_check_response_status", response.status_code, 'usebouncer_check')

        pushalert('available_email_num', available_email_num, 'usebouncer_check')

        time.sleep(1 * 60 * 60)


if __name__ == '__main__':
    useboncer_check()
