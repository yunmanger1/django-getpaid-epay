import base64
try:
    from urllib.parse import quote
except:
    from urllib import quote

import xmltodict

from .signing import sign_string


ORDER_TPL = (
    """<merchant cert_id="{cert_id}" name="{merchant_name}">"""
    """<order order_id="{order_id:06d}" amount="{amount}" currency="{currency_code}">"""
    """<department merchant_id="{merchant_id}" amount="{amount}"/></order></merchant>""")


COMMAND_TPL = (
    """<merchant id="{merchant_id}"><command type="{command}"/>"""
    """<payment reference="{reference_id}" approval_code="{approval_code}" orderid="{order_id}" """
    """amount="{amount}" currency_code="{currency_code}"/><reason>{reason}</reason></merchant>""")


STATUS_TPL = """<merchant id="{merchant_id}"><order id="{order_id}"/></merchant>"""


DOC_TPL = ("""<document>{document}<merchant_sign type="RSA">{signature}</merchant_sign></document>""")


def payment_auth(order_id, amount, currency_code, cert_id, merchant_id, merchant_name, private_key, passphrase):
    """
        <document>
            <merchant cert_id="1231232" name="Test Shop">
                <order order_id="000001" amount="1000.00" currency="398">
                    <department merchant_id="23124" amount="1000.00"></department>
                </order>
            </merchant>
            <merchant_sign type="RSA">SIGNATURE</merchant_sign>
        </document>

    :param order_id:
    :param amount:
    :param currency_code:
    :param cert_id:
    :param merchant_id:
    :param merchant_name:
    :return: base64 encoded signed xml document
    """
    order_xml = ORDER_TPL.format(
        order_id=order_id,
        amount=amount,
        cert_id=cert_id,
        currency_code=currency_code,
        merchant_name=merchant_name,
        merchant_id=merchant_id
    )
    signature = sign_string(order_xml, private_key=private_key, passphrase=passphrase)
    document_xml = DOC_TPL.format(document=order_xml, signature=signature)
    return document_xml


def payment_control(
        command, reference, approval_code, order_id, amount, currency_code,
        merchant_id, private_key, passphrase=None, reason=None):
    if not reason:
        reason = ''
    order_xml = COMMAND_TPL.format(
        command=command,
        order_id=order_id,
        reference_id=reference,
        approval_code=approval_code,
        amount=amount,
        reason=reason,
        currency_code=currency_code,
        merchant_id=merchant_id)
    signature = sign_string(order_xml, private_key=private_key, passphrase=passphrase)
    document_xml = DOC_TPL.format(document=order_xml, signature=signature)
    print(document_xml)
    return document_xml


def payment_status(order_id, merchant_id, private_key, passphrase=None):
    order_xml = STATUS_TPL.format(order_id=order_id, merchant_id=merchant_id)
    signature = sign_string(order_xml, private_key=private_key, passphrase=passphrase)
    document_xml = DOC_TPL.format(document=order_xml, signature=signature)
    return document_xml


def decode(value):
    return value.decode('string_escape')


def parse(xml):
    """

    :param value:
    :return: an ordered dict
    """
    # dirty hack around EPAY bug
    # KKB, what a hell? <p><Error></Error>
    if '<p>' in xml:
        xml = '<hack>{}</hack>'.format(xml.replace('<p>', ''))
    res = xmltodict.parse(
        xml, attr_prefix='', cdata_key='body',
        postprocessor=lambda path, key, value: (key.lower(), value))
    if 'hack' in res:
        return res['hack']
    return res


_BANK_OFFSET = len('</bank>')


def get_letter(xml):
    """

    :param xml:
    :return: everything between <bank> tag
    """
    try:
        left, right = xml.index('<bank '), xml.index('</bank>') + _BANK_OFFSET
        return xml[left:right]
    except ValueError:
        return None


def get_bank_signature(doc):
    if 'bank_sign' in doc['document']:
        return doc['document']['bank_sign']['body']
    # dirty hack around strange KKB response format
    if 'merchant' in doc['document'] and 'bank_sign' in doc['document']['merchant']:
        return doc['document']['merchant']['bank_sign']['body']


def get_bank(doc):
    if 'bank' in doc:
        return doc['bank']
    # dirty hack around strange KKB response format
    if 'merchant' in doc and 'bank' in doc['merchant']:
        return doc['merchant']['bank']


def parse_response(value):
    response = decode(value)
    result = parse(response)
    if 'error' in result:
        return result, None, None
    return result['document'], get_bank_signature(result), get_letter(response)


def b64(value):
    return base64.encodestring(value)


def urlquote(value):
    return quote(value)


# def request_url(link):
#     req = urllib.Request(link)
#     sock = urllib.urlopen(req)
#     response = sock.read()
#     sock.close()
#     return response.strip()


def _print(obj):
    import json
    print(json.dumps(obj, indent=2))
