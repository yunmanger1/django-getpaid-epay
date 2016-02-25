========
Usage
========


.. note:: I assume that you already have django-getpaid installed and configured

Install django-getpaid-epay::

    pip install django-getpaid-epay


Add ``epay`` to ``INSTALLED_APPS`` and ``GETPAID_BACKENDS`` in your django project. Do not forget to configure the ``GETPAID_ORDER_MODEL`` setting.


Run migration::

   ./manage.py migrate

Configuration
-------------

.. note:: Putting your private keys in codebase is bad practice. Keep them outside of your project folder.

Here is minimal configuration::


    GETPAID_BACKENDS_SETTINGS = {
        'epay' : {
            "key_passphrase" : 'your private key passphrase',  # optional
            "merchant_private_key" : 'path to your private key',
            "merchant_id" :  "92061101",
            "merchant_name" : "Test Shop",
            "merchant_cert_id" : "00c182b189",
            "kkb_pub_key": 'path to Kazkom Public Key (kkbca.pem)',  # optional
            "modify_order_id": lambda id: id + 100000,  # optional
            "unmodify_order_id": lambda id: id - 100000,  # optional
            'scheme': 'http',  # optional
            'testing' : True,  # optional
        },
    }


Explanation:

 * ``key_passphrase`` - Your private key passphrase. This can be omitted if you have removed passphrase, see below
 * ``merchant_private_key`` - path to private key in file system.
 * ``merchant_id`` - your merchant id
 * ``merchant_name`` - your merchant name
 * ``merchant_cert_id`` - your certificate id
 * ``kkb_pub_key`` - path to kkb public key in file system
 * ``modify_order_id`` - a function to modify order id sent to epay
 * ``unmodify_order_id`` - the reverse of ``modify_order_id``. Used when order id is receive from epay.
 * ``scheme`` - Use http or https protocol for callback and fallback urls
 * ``testing`` - boolean. use testing or production epay server

.. note:: order_id sent to epay should be unique. You cannot authenticate two different payments with same id. Sometimes it's useful to be able to modify ``order_id`` sent to epay, you can do it with ``modify_order_id`` and ``unmodify_order_id`` settings.




Keys
----

To remove passphrase from private key::

  $ openssl rsa -in cert.prv -out cert.pem




Testing callback
----------------

To test Epay payment backend in real conditions you need a public address so that bank processing can request your callback url. You can use ``ngrok`` to get temporary public address during development or testing::

  $ ngrok http 8000
  $ GETPAID_SITE_DOMAIN=1d258d87.ngrok.io ./manage.py runserver
