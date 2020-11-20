#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from setuptools import setup, find_packages


setup(name="vlab-api-gateway",
      author="Nicholas Willhite,",
      author_email='willnx84@gmail.com',
      version='2020.11.20',
      packages=find_packages(),
      description="Routes requests to vLab services",
      install_requires=['gunicorn', 'gevent', 'ujson', 'cffi>=1.11.5'],
      )
