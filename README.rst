##########
vLab Proxy
##########

Unifies all the different vLab services behind a single URL. `HAProxy <http://www.haproxy.org>`_
is used in this service to:

- Perform layer-7 routing
- TLS termination
- Load balancing
- HTTP redirects to HTTPS

.. warning::

   Make sure to replace the TLS certificate when running in production!

To make life easier while testing, the docker image contains a self-signed TLS
certificate. In production, you must replace the self-signed cert. The cert must
be in `PEM <https://en.wikipedia.org/wiki/Privacy-enhanced_Eletronic_Mail>`_
format. The TLS cert is located at ``/etc/vlab/proxy/server.pem``.


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
         - /path/to/proxy/server.pem:/etc/vlab/proxy/server.pem
