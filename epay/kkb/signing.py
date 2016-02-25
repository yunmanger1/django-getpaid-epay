import M2Crypto
import base64


def sign_string(string, private_key, passphrase=None):
    signEVP = M2Crypto.EVP.load_key_string(private_key, callback=lambda s: passphrase)
    signEVP.sign_init()
    signEVP.sign_update(string)
    signature = signEVP.sign_final()
    signature = signature[::-1]
    return base64.encodestring(signature)


def verify_sign(sign, letter, public_key):
    rawsign = base64.decodestring(sign)[::-1]
    pubkey = M2Crypto.X509.load_cert_string(public_key).get_pubkey()
    pubkey.verify_init()
    pubkey.verify_update(letter)
    return pubkey.verify_final(rawsign)
