# -*- coding: utf-8 -*-

import logging

from django.apps import apps
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.generic import View
from django.views.generic.detail import DetailView

from epay.kkb import exceptions
from . import PaymentProcessor

logger = logging.getLogger(__name__)


class EpayCallback(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        if 'response' not in request.POST:
            return HttpResponseBadRequest("400 Bad Request")
        try:
            PaymentProcessor.callback(request.POST['response'])
            return HttpResponse('OK')
        except exceptions.VerificationError:
            return HttpResponseBadRequest("400 Bad Request")
        except exceptions.EpayError:
            return HttpResponseBadRequest("400 Bad Request")


class PaymentDetail(DetailView):
    model = apps.get_model("getpaid", "payment")
    template_name = 'epay/payment_detail.html'

    def get_queryset(self):
        qs = super(PaymentDetail, self).get_queryset()
        return qs.select_related('epaypayment')

    def get_context_data(self, object, **kwargs):
        ctx = super(PaymentDetail, self).get_context_data(object=object, **kwargs)
        ctx.update({
            "response": PaymentProcessor.get_status(object.pk)
        })
        return ctx
