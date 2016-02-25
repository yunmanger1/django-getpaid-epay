from epay.kkb.utils import parse


def test_nasty_kkb_response():
    assert parse("<p><Error>Hello</Error>") == {"error": "Hello"}
    assert parse("<Error>Hello</Error><p><Error>World</Error>") == {"error": ["Hello", "World"]}
