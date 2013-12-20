import unittest
from address import Address
from reparse.tools.expression_checker import check_expression
import yaml

from address_corpus import address_corpus as corpus


class venue_address_test(unittest.TestCase):
    def setUp(self):
        self.parser = Address()

    def test_expression_examples(self):
        for test in corpus:
            result = self.parser.parse(test)
            self.assertNotEqual(result, None, "No match for: {}".format(test))
            self.assertTrue(any(result), "No match for: {}".format(test))

    def test_expressions(self):
        with open("parse/address/expressions.yaml", 'r') as f:
            check_expression(self, yaml.load(f))