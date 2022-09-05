#!/usr/local/bin/python3.9

from pushgateway_client import client

def pushalert(metric_name="test",metric_value="-1",job_name="job_name"):
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

def test():
    pushalert("test1_status","0","test1")

test()
