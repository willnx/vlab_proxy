# -*- coding: UTF-8 -*-
"""Configuration file for running gunicorn webserver"""

bind='0.0.0.0'
worker_class='gevent'
workers=1
name='vlab-api-gateway'
