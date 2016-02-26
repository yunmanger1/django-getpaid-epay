=============================
django-getpaid-epay
=============================

.. image:: https://badge.fury.io/py/django-getpaid-epay.png
    :target: https://badge.fury.io/py/django-getpaid-epay

.. .. image:: https://travis-ci.org/yunmanger1/django-getpaid-epay.png?branch=master
..     :target: https://travis-ci.org/yunmanger1/django-getpaid-epay

A django-getpaid payment backend for Kazkommertsbank Epay

.. image:: _static/logo.png
    :target: https://epay.kkb.kz

Documentation
-------------

The full documentation is at https://django-getpaid-epay.readthedocs.org.


Features
--------

* Authenticate payment
* Capture blocked money from admin
* Reverse payment from admin
* Refund payment from admin
* Check status from admin


Dependencies
------------

Here is a list of dependecies::

   # obvious
   django
   django-getpaid

   M2Crypto
   django-model-utils
   xmltodict
   requests



.. warning:: You might need to install some system packages to compile M2Crypto. What to install?



Quickstart
----------

Install django-getpaid and then install django-getpaid-epay::

    pip install django-getpaid-epay


Add ``epay`` to ``INSTALLED_APPS`` and ``GETPAID_BACKENDS`` in your django project. Do not forget to configure the ``GETPAID_ORDER_MODEL`` setting.


Run migration::

   ./manage.py migrate



Basic configuration
-------------------

Here is minimal configuration::


    GETPAID_BACKENDS_SETTINGS = {
        'epay' : {
            "key_passphrase" : 'your private key passphrase',  # can be omitted if you have removed passphrase
            "merchant_private_key" : 'path to your private key',
            "merchant_id" :  "92061101",
            "merchant_name" : "Test Shop",
            "merchant_cert_id" : "00c182b189"
            # "kkb_pub_key": 'path to Kazkom Public Key (kkbca.pem)',  # optional
            # "modify_order_id": lambda id: id + 100000,
            # "unmodify_order_id": lambda id: id - 100000,
            # 'scheme': 'http',
            # 'testing' : True,       # optional
        },
    }


.. Running Tests
.. --------------
..
.. Does the code actually work?
..
.. ::
..
..     source <YOURVIRTUALENV>/bin/activate
..     (myenv) $ pip install -r requirements-test.txt
..     (myenv) $ python runtests.py


Credits
---------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
