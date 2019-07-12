#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
TODO
"""
from setuptools import setup, find_packages


setup(name="vlab-api-gateway",
      author="Nicholas Willhite,",
      author_email='willnx84@gmail.com',
      version='2019.07.12',
      packages=find_packages(),
      description="Routes requests to vLab services",
      install_requires=['gunicorn', 'gevent', 'ujson', 'cffi>=1.11.5'],
      )
