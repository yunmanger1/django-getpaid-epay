from django.apps import apps
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from epay.kkb.exceptions import EpayError
from . import PaymentProcessor


def epay_payment_status(obj):
    return '<a href="{}">{}</a>'.format(
        reverse("epay:status", kwargs={'pk': obj.id}),
        _("Check status")
    )

epay_payment_status.allow_tags = True
epay_payment_status.short_description = _("EPAY status")


def complete_epay_payment(modeladmin, request, queryset):
    payment = queryset.select_related('epaypayment').first()

    try:
        payment.epaypayment
    except ObjectDoesNotExist:
        messages.error(request, _("This payment has no epay payment associated with it"))
        return None

    try:
        PaymentProcessor.completed(payment.id)
        messages.info(request, _("Payment successfully completed"))
    except EpayError as e:
        messages.error(request, _("Request failed: %s") % unicode(e))
complete_epay_payment.short_description = _("Complete epay payment")


def refund_epay_payment(modeladmin, request, queryset):
    payment = queryset.select_related('epaypayment').first()

    try:
        epay_payment = payment.epaypayment
    except ObjectDoesNotExist:
        messages.error(request, _("This payment has no epay payment associated with it"))
        return None

    try:
        PaymentProcessor.refunded(payment.id)
        messages.info(request, _("Payment successfully refunded"))
    except EpayError as e:
        messages.error(request, _("Request failed: %s") % unicode(e))

refund_epay_payment.short_description = _("Refund epay payment")


def reverse_epay_payment(modeladmin, request, queryset):
    payment = queryset.select_related('epaypayment').first()

    try:
        epay_payment = payment.epaypayment
    except ObjectDoesNotExist:
        messages.error(request, _("This payment has no epay payment associated with it"))
        return None

    try:
        PaymentProcessor.reversed(payment.id)
        messages.info(request, _("Payment successfully reversed"))
    except EpayError as e:
        messages.error(request, _("Request failed: %s") % unicode(e))

reverse_epay_payment.short_description = _("Reverse epay payment")


def check_epay_payment(modeladmin, request, queryset):
    payment = queryset.select_related('epaypayment').first()
    EpayPayment = apps.get_model('epay', 'epaypayment')

    try:
        payment.epaypayment
    except ObjectDoesNotExist:
        EpayPayment.objects.create(payment=payment)

    try:
        PaymentProcessor.update_status(payment.id)
        messages.info(request, _("Payment successfully updated"))
    except EpayError as e:
        messages.error(request, _("Request failed: %s") % unicode(e))

check_epay_payment.short_description = _("Check epay payment")
