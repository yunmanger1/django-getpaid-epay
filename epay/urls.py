# -*- coding: utf-8 -*-
from django.conf.urls import include, patterns, url

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction

from .views import EpayCallback, PaymentDetail
from . import PaymentProcessor

has_perm = PaymentProcessor.get_backend_setting("has_perm", lambda u: u.is_superuser)


my_urls = patterns(
    '',
    url(r'^callback/$', csrf_exempt(require_POST(transaction.atomic(EpayCallback.as_view()))), name='postlink'),
    url(r'^status/(?P<pk>\d+)/$', user_passes_test(has_perm)(PaymentDetail.as_view()), name='status'),
)


urlpatterns = patterns(
    '',
    url(r'', include(my_urls, namespace='epay'))
)
