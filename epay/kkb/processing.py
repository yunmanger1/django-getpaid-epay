import requests

from . import utils
from . import signing
from . import exceptions


def id_modify(self, id):
    return id


class Epay(object):

    BACKEND_TEST_GATEWAY_BASE_URL = u'https://testpay.kkb.kz'
    BACKEND_GATEWAY_BASE_URL = u'https://epay.kkb.kz'
    BACKEND_POST_URI = '/jsp/process/logon.jsp'
    BACKEND_CONFIRM_URI = '/jsp/remote/control.jsp'
    BACKEND_CHECK_URI = '/jsp/remote/checkOrdern.jsp'
    BACKEND_ACCEPTED_CURRENCY_DICT = {
        'KZT': 398,
        'USD': 840,
        'EUR': 978,
    }
    BACKEND_ACCEPTED_CURRENCY = (u'KZT', u'USD', u'EUR')

    modify_order_id = id_modify
    unmodify_order_id = id_modify
    key_passphrase = None
    testing = False
    private_key = None
    kkb_key = None
    merchant_name = "Demo Shop"
    merchant_id = "92061101"
    merchant_cert_id = "00c182b189"
    auto_capture = False

    def __init__(self, **kw):
        for key, value in kw.items():
            if key.startswith('get_'):
                continue
            if key in ('modify_order_id', 'unmodify_order_id'):
                setattr(self, key, lambda self, id: value(id))
            setattr(self, key, value)

    def get_number_for_currency(self, currency):
        return self.BACKEND_ACCEPTED_CURRENCY_DICT.get(currency, None)

    def sign_order(self, payment_id, amount, currency="KZT"):
        return utils.b64(utils.payment_auth(
            order_id=self.modify_order_id(payment_id),
            amount=amount,
            currency_code=self.get_number_for_currency(currency),
            merchant_id=self.merchant_id,
            merchant_name=self.merchant_name,
            cert_id=self.merchant_cert_id,
            private_key=self.private_key,
            passphrase=self.key_passphrase,
        ))

    def get_command_url(self, command, payment_id, amount, approval_code, reference, currency="KZT", reason=None):
        """

        :param command: one of complete, reverse, refund
        :param payment_id:
        :param amount:
        :param approval_code:
        :param reference:
        :param currency:
        :param reason:
        :return:
        """
        quoted_xml = utils.urlquote(utils.payment_control(
            command,
            reference=reference,
            approval_code=approval_code,
            order_id=self.modify_order_id(payment_id),
            amount=amount,
            reason=reason,
            currency_code=self.get_number_for_currency(currency),
            merchant_id=self.merchant_id,
            private_key=self.private_key,
            passphrase=self.key_passphrase,
        ))
        url = self.get_gateway_base_url() + self.BACKEND_CONFIRM_URI + "?" + quoted_xml
        if self.testing:
            url = url.replace('https', 'http')
        return url

    def get_status_url(self, payment_id):
        quoted_xml = utils.urlquote(utils.payment_status(
            order_id=self.modify_order_id(payment_id),
            merchant_id=self.merchant_id,
            private_key=self.private_key,
            passphrase=self.key_passphrase,
        ))
        url = self.get_gateway_base_url() + self.BACKEND_CHECK_URI + "?" + quoted_xml
        if self.testing:
            url = url.replace('https', 'http')
        return url

    def get_gateway_base_url(self):
        if self.testing:
            return self.BACKEND_TEST_GATEWAY_BASE_URL
        return self.BACKEND_GATEWAY_BASE_URL

    def handle_response(self, response):
        result, signature, letter = utils.parse_response(response)
        if 'error' in result:
            raise exceptions.RequestError(result['error'])
        if not signing.verify_sign(signature, letter, self.kkb_key):
            raise exceptions.VerificationError("Failed to verify signature")
        return utils.get_bank(result)

    def get_gateway_url(self):
        return self.get_gateway_base_url() + self.BACKEND_POST_URI

    def capture(self, payment_id, amount, approval_code, reference, currency="KZT"):
        url = self.get_command_url("complete", payment_id, amount, approval_code, reference, currency)
        response = requests.get(url)
        response = self.handle_response(response.content)
        if response['response']['code'] != '00':
            raise exceptions.EpayError(response['response']['message'])
        return response

    def get_status(self, payment_id):
        url = self.get_status_url(payment_id)
        response = requests.get(url)
        response = self.handle_response(response.content)
        if 'response' not in response:
            raise exceptions.EpayError("Something is wrong")
        return response

    def refund(self, payment_id, amount, approval_code, reference, currency="KZT"):
        url = self.get_command_url(
            "refund", payment_id, amount, approval_code, reference, currency, reason="Client initiative")
        response = requests.get(url)
        response = self.handle_response(response.content)
        if response['response']['code'] != '00':
            raise exceptions.EpayError(response['response']['message'])
        return response

    def cancel(self, payment_id, amount, approval_code, reference, currency="KZT"):
        url = self.get_command_url(
            "reverse", payment_id, amount, approval_code, reference, currency, reason="Client initiative")
        response = requests.get(url)
        print(response.status_code, response.content, url)
        response = self.handle_response(response.content)
        if response['response']['code'] != '00':
                raise exceptions.EpayError(response['response']['message'])

        return response
