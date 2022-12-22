import json
import logging
import re
import time

import requests
from pushgateway_client import client

logging.basicConfig(level=logging.INFO,
                    filename='usebouncer_check.log',
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


def delete_monitor_instance():
    try:
        # 监控脚本运行前，先清理pushgateway中上由上一个监控实例推送的监控数据，以避免误报
        time.sleep(30)
        response = requests.get('http://pushgateway.voiladev.xyz:32684/metrics')
        content = str(response.content)
        instance = re.findall(r'instance=[\'|\"](monitorscripts.+?)[\'|\"]', content)
        uniq_instance = []
        job_name = ["usebouncer_check"]

        # instance去重
        for i in instance:
            if i not in uniq_instance:
                uniq_instance.append(i)
        for job in job_name:
            for j in uniq_instance:
                url = "http://pushgateway.voiladev.xyz:32684/metrics/job/" + job + "/instance/" + j + "/env/prod"
                response = requests.delete(url)
                logging.info(
                    "pushgateway job is %s, delete instance %s successfully, url is %s, response.status_code is %s",
                    job, j, url, response.status_code)
    except Exception as e:
        logging.info(e)


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

        try:

            response = requests.get(url, headers=header)

            available_email_num = json.loads(response.text).get('credits')

            logging.info('response.status_code is %s, available_email_num is %s', response.status_code,
                         available_email_num)

            pushalert("usebouncer_check_response_status", response.status_code, 'usebouncer_check')

            pushalert('available_email_num', available_email_num, 'usebouncer_check')
        except Exception as e:
            logging.info(e)

        time.sleep(1 * 60 * 60)


if __name__ == '__main__':
    delete_monitor_instance()
    useboncer_check()
