##########
vLab Proxy
##########

Unifies all the different vLab services behind a single URL. `NGINX <https://www.nginx.com/>`_
is used in this service to:

- Perform layer-7 routing
- TLS termination
- Load balancing
- HTTP redirects to HTTPS

.. warning::

   Make sure to replace the TLS certificate when running in production!

To make life easier while testing, the docker image contains a self-signed TLS
certificate. In production, you **must** replace the self-signed cert and key.
The key and cert are expected to be at the following paths with the following names:

- Key : /etc/ssl/server.key
- Cert: /etc/ssl/server.crt


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
