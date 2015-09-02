import unittest
from requests import get


class WebServiceTests(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://localhost:5000/getinfo?"
        #self.base_url = "http://magicsearch.philipcote.com/getinfo?"

    def _general_tests(self, res):
        self.assertIsNotNone(res, "Should be a non-none result")

        self.assertTrue("results" in res.json(), "There should be a results key in the res object")
        data_list = res.json().get("results")
        self.assertIsInstance(data_list, list, "There should be a data list that isn't none")
        self.assertTrue(len(data_list) > 0, "There should be data in this list")

    def _get_data(self, arg):
        url = "{}{}".format(self.base_url, arg)
        res = get(url)
        return res

    def test_strength(self):

        res = self._get_data("power=1")
        self._general_tests(res)
        for card in res.json().get("results"):
            self.assertTrue(card["power"] == "1", "Card power is wrong in this test case: {}".format(card))

        res = self._get_data("toughness=2")
        self._general_tests(res)
        for card in res.json().get("results"):
            self.assertTrue(card["toughness"] == "2", "Card toughness is wrong in this test case: {}".format(card))

        res = self._get_data("toughness=6&power=5")
        self._general_tests(res)
        for card in res.json().get("results"):
            self.assertTrue(card.get("power") == "5", "Card power is wrong in this test case: {}".format(card))
            self.assertTrue(card.get("toughness") == "6", "Card toughness is wrong in this test case: {}".format(card))


    def test_color(self):
        res = self._get_data("color=Red")
        self._general_tests(res)

        for card in res.json().get("results"):
            self.assertTrue(card.get("color") == "Red", "This card should be red and it's not. {}".format(card))

    def test_loyalty(self):
        res = self._get_data("loyalty=3")
        self._general_tests(res)

        for card in res.json().get("results"):
            self.assertTrue(card.get("loyalty") == "3", "This card loyalty should be 3... {}".format(card))

    def test_text(self):
        import requests.utils
        arg = requests.utils.quote("enters the battlefield")
        res = self._get_data("text={}".format(arg))
        self._general_tests(res)

        for card in res.json().get("results"):
            self.assertTrue("enters the battlefield" in card.get("text"), "'enters the battlefield' should be in the text for this card... {}".format(card))

    def tearDown(self):
        self.base_url = None


if __name__ == '__main__':
    unittest.main()