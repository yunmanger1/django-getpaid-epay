# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from getpaid.abstract_mixin import AbstractMixin
from model_utils.choices import Choices

from . import PaymentProcessor


EPAY_STATUSES = Choices(
    (0, "new", _("waiting for payment")),
    (1, "inblock", _("money are blocked")),
    (2, "captured", _("paid")),
    (3, "cancelled", _("cancelled")),
    (4, "refunded", _("refunded")),
    (5, "failed", _("failed")),
)


def int_or_none(val):
    try:
        return int(val)
    except ValueError:
        return None


class EpayPaymentFactory(models.Model, AbstractMixin):
    """

    "@name": "GERMAN ILIN",
    "@mail": "germanilyin@gmail.com",
    "@phone": "",

    "@merchant_id": "92061101",
    "@card": "548318-XX-XXXX-0293",
    "@amount": "1000.0000",
    "@reference": "160216002802",
    "@approval_code": "002802",
    "@response_code": "00",
    "@Secure": "Yes",
    "@card_bin": "KAZ",
    "@c_hash": "D643983890D0003EA973E88A346CDDBE"

    """

    statuses = EPAY_STATUSES

    merchant_id = models.CharField(max_length=15, blank=True)
    card = models.CharField(max_length=len("548318-XX-XXXX-0293"), blank=True)
    reference = models.CharField(max_length=15, blank=True)
    approval_code = models.CharField(max_length=15, blank=True)
    response_code = models.CharField(max_length=5, blank=True)
    is_secure = models.BooleanField(default=True, blank=True)
    card_bin = models.CharField(max_length=10, blank=True)
    c_hash = models.CharField(max_length=len("D643983890D0003EA973E88A346CDDBE") + 4, blank=True)
    customer_name = models.CharField(max_length=50, blank=True)
    customer_mail = models.CharField(max_length=75, blank=True)
    customer_phone = models.CharField(max_length=20, blank=True)
    is_payment = models.BooleanField(default=True)
    status = models.IntegerField(blank=True, null=True)
    result = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True

    @classmethod
    def contribute(cls, payment):
        return {'payment': models.OneToOneField(payment)}

    def update_from_kkb(self, response=None):
        if not response:
            response = PaymentProcessor.get_status(self.payment_id)
        self.is_payment = response['payment'].lower() == "true"
        self.status = int_or_none(response['status'])
        self.result = int_or_none(response['result'])
        self.approval_code = response['approval_code']
        self.ping_status()
        self.save()

    def ping_status(self):
        new_status = self.get_status()
        if new_status == self.statuses.cancelled:
            self.payment.change_status('cancelled')
        if new_status == self.statuses.failed:
            self.payment.change_status('failed')
        if new_status == self.statuses.refunded:
            self.payment.change_status('cancelled')
        if new_status == self.statuses.new:
            self.payment.change_status('in_progress')
        if new_status == self.statuses.captured:
            self.payment.change_status('paid')

    @staticmethod
    def import_or_update(response, payment_id):
        try:
            epay_payment = EpayPayment.objects.select_related('payment').get(payment_id=payment_id)
            epay_payment.update_from_kkb(response)
        except EpayPayment.DoesNotExist:
            raise NotImplementedError("Need to implement import part")

    def get_status(self):
        return EpayPaymentFactory.calc_status(self.is_payment, self.status, self.result)

    @staticmethod
    def calc_status(payment, status, result):
        if not payment:
            if status == 2:
                return EPAY_STATUSES.cancelled
            return EPAY_STATUSES.failed
        if payment:
            if status == 0:
                return EPAY_STATUSES.new
            if status == 2:
                return EPAY_STATUSES.captured


EpayPayment = None


def build_models(payment_class):
    global EpayPayment

    class EpayPayment(EpayPaymentFactory.construct(payment_class)):
        pass
    return [EpayPayment]
