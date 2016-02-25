import sys

try:
    from django.conf import settings
    from django.test.utils import get_runner

    settings.configure(
        DEBUG=True,
        USE_TZ=True,
        STATIC_URL='/static/',
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
            }
        },
        ROOT_URLCONF="epay.urls",
        INSTALLED_APPS=[
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sites",
            "getpaid",
            "tests.app",
            "epay",
        ],
        SITE_ID=1,
        MIDDLEWARE_CLASSES=(),
        GETPAID_BACKENDS = ('epay',),
        GETPAID_ORDER_MODEL = 'app.Order',
        GETPAID_SITE_DOMAIN = 'localhost:8000',
        GETPAID_BACKENDS_SETTINGS = {
            'epay' : {
                # "key_passphrase" : env("EPAY_PASSPHRASE", default=None),
                # "merchant_private_key" : env("EPAY_PRIVATE_KEY", default="keys/cert.pem"),
                "merchant_id" : "92061101",
                "merchant_name" : "Demo Shop",
                "merchant_cert_id" : "00c182b189",
                # "kkb_pub_key": env("EPAY_KKB_PUBLIC_KEY", default="keys/kkbca.pem"),
                "modify_order_id": lambda id: id,
                "unmodify_order_id": lambda id: id,
                # "modify_order_id": lambda id: id + 100000,
                # "unmodify_order_id": lambda id: id - 100000,
                'scheme': 'http',
                'signing' : True,       # optional
                'testing' : True,       # optional
            },
        }
    )

    try:
        import django
        setup = django.setup
    except AttributeError:
        pass
    else:
        setup()

except ImportError:
    import traceback
    traceback.print_exc()
    raise ImportError("To fix this error, run: pip install -r requirements-test.txt")


def run_tests(*test_args):
    if not test_args:
        test_args = ['tests']

    # Run tests
    TestRunner = get_runner(settings)
    test_runner = TestRunner()

    failures = test_runner.run_tests(test_args)

    if failures:
        sys.exit(bool(failures))


if __name__ == '__main__':
    run_tests(*sys.argv[1:])
