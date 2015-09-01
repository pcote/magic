import unittest
from requests import get


class WebServiceTests(unittest.TestCase):

    def setUp(self):
        self.base_url = "http://magicsearch.philipcote.com/getinfo?"

    def _general_tests(self, res):
        self.assertIsNotNone(res, "Should be a non-none result")
        data_list = res.json().get("results")
        self.assertIsInstance(data_list, list, "There should be a data list that isn't none")
        self.assertTrue(len(data_list) > 0, "There should be data in this list")

    def _get_data(self, arg):
        url = "{}{}".format(self.base_url, "power=1")
        res = get(url)
        return res

    def test_strength(self):
        res = self._get_data("power=1")
        self._general_tests(res)
        res = self._get_data("toughness=2")
        self._general_tests(res)
        res = self._get_data("toughness=6&power=6")
        self._general_tests(res)

    def test_color(self):
        res = self._get_data("color=Red")
        self._general_tests(res)

    def test_loyalty(self):
        res = self._get_data("loyalty=3")
        self._general_tests(res)

    def test_text(self):
        import requests.utils
        arg = requests.utils.quote("enters the battlefield")
        res = self._get_data("loyalty={}".format(arg))
        self._general_tests(res)

    def tearDown(self):
        self.base_url = None


if __name__ == '__main__':
    unittest.main()