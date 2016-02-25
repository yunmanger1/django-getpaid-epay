from __future__ import unicode_literals


from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible
from django.core.urlresolvers import reverse


import getpaid


ORDER_STATUSES = (
    (0, 'new'),
    (1, 'paid'),
    (3, 'canceled'),
    (3, 'failed'),
)

@python_2_unicode_compatible
class Order(models.Model):
    statuses = ORDER_STATUSES
    currency = "KZT"

    amount = models.DecimalField(_("amount"), decimal_places=4, max_digits=20)
    status = models.IntegerField(choices=statuses, default=0)

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")

    def is_ready_for_payment(self):
        return self.status == 0

    def get_absolute_url(self):
        return '/order/{}'.format(self.pk)

    def __str__(self):
        return str(self.id)


getpaid.register_to_payment(Order, unique=False, related_name='payments')


from getpaid import signals

def payment_status_changed_listener(sender, instance, old_status, new_status, **kwargs):
    """
    Here we will actually do something, when payment is accepted.
    E.g. lets change an order status.
    """
    if old_status != 'paid' and new_status == 'paid':
        # Ensures that we process order only once
        instance.order.status = 1
        instance.order.save()

    # if old_status != 'paid' and new_status == 'paid':
    #     # Ensures that we process order only once
    #     instance.order.status = ORDER_STATUSES.paid
    #     instance.order.save()

signals.payment_status_changed.connect(payment_status_changed_listener)


def overrider_user_data(sender, order, user_data, *args, **kwargs):
    # user_data.update({'email': order.user.})
    pass

signals.user_data_query.connect(overrider_user_data)


def new_payment_query_listener(sender, order=None, payment=None, **kwargs):
    """
    Here we fill only two obligatory fields of payment, and leave signal handler
    """
    payment.amount = order.amount
    payment.currency = order.currency

signals.new_payment_query.connect(new_payment_query_listener)
