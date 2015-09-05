from requests import get
import unittest
"""
Nose-dependent unit tests for testing the web service calls.
"""


def call_service(endpoint, json_args=None):
    if json_args:
        res = get("http://localhost:5000{}".format(endpoint), json=json_args)
    else:
        res = get("http://localhost:5000{}".format(endpoint))
    json_data = res.json()
    results = json_data.get("results")
    return results


def test_get_card():
    res = get("http://localhost:5000/card/3")
    print(res.json())
    print(res.json().get("results"))
    card = call_service("/card/3")
    key_attrs = res.json().get("results").keys()
    print(key_attrs)
    assert("name" in card.keys())
    assert("set_code" in card.keys())


def test_card_strength():
    args = dict(power=2, toughness=2)
    cards = call_service("/strength", json_args=args)
    card = cards[0]
    keys = card.keys()
    assert("power" in keys)
    assert("toughness" in keys)
    assert(card.get("power") == "2")
    assert(card.get("toughness") == "2")


def test_set_info():
    res = call_service("/setinfo/RTR")
    assert("name" in res.keys())
    assert("code" in res.keys())
    assert(res.get("code") == "RTR")


def test_loyalty():
    cards = call_service("/loyalty/2")
    card = cards[0]
    assert("loyalty" in card.keys())
    assert(card.get("loyalty") == 2)


def test_color_search():
    cards = call_service("/color", json_args=dict(color="Red"))
    card = cards[0]
    assert("color_name" in card)
    assert(card.get("color_name") == "Red")


def test_text_search():
    test_phrase = "enters the battlefield"
    cards = call_service("/text", json_args=dict(text=test_phrase))
    card = cards[0]
    assert("text" in card)
    assert(test_phrase in card.get("text"))


if __name__ == '__main__':
    unittest.main()
