.. image:: https://travis-ci.org/willnx/vlab_proxy.svg?branch=master
   :target: https://travis-ci.org/willnx/vlab_proxy

##########
vLab Proxy
##########

Unifies all the different vLab services behind a single URL. It's comprised of
two different subsystems:

- NGINX
- A custom API Gateway application

*****
NGINX
*****

`NGINX <https://www.nginx.com/>`_ is used in this service for:

- TLS termination
- HTTP redirects to HTTPS

.. warning::

   Make sure to replace the TLS certificate when running in production!

To make life easier while testing, the docker image contains a self-signed TLS
certificate. In production, you **must** replace the self-signed cert and key.
The key and cert are expected to be at the following paths with the following names:

- Key : /etc/ssl/server.key
- Cert: /etc/ssl/server.crt

Behind NGINX is the vLab API Gateway. This service contains all the logic on
how to connect a client's request with the correct back-end server.


***********
API Gateway
***********

An `API Gatway <https://microservices.io/patterns/apigateway.html>`_ is a pattern
used to map front-end clients to back-end services. The goal of this abstraction
is to prevent *"how to find a service"* business logic from living in a client
application.

The vLab API is broken up across multiple back-end services, and user-specific
instances of a NATing firewall. The API Gateway uses layer-7 routing to find
the correct back-end service. Finding the correct NATed firewall is done via
DNS resolution of the `DDNS <https://en.wikipedia.org/wiki/Dynamic_DNS>`_ record
of that NATed firewall.


*********
Deploying
*********

Here's an example docker-compose file, that will use your configured TLS cert:

.. code-block:: yaml

   version: '3'
   services:
     vlab-proxy:
       ports:
         - "80:80"
         - "443:443"
       image:
         willnx/vlab-proxy
       volume:
         - /path/to/proxy/my.vlab.crt:/etc/ssl/server.crt
         - /path/to/proxy/my.vlab.key:/etc/ssl/server.key
     api-gateway:
       image:
         willnx/vlab-api-gateway
       dns:
         - <ip of vLab server>
       enviroment:
         - PRODUCTION=<true/false>
         - VLAB_FQDN=<DNS name of the vLab server>
