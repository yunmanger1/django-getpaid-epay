#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_django-getpaid-epay
------------

Tests for `django-getpaid-epay` models module.
"""

from django.test import TestCase
from django.apps import apps

# from epay import models


class TestEpay(TestCase):

    def setUp(self):
        Order = apps.get_model('app', 'Order')
        self.order = Order(amount=1000)
        self.order.save()


    def test_something(self):
        pass

    def tearDown(self):
        pass
