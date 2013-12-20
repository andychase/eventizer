import unittest
from corpus import corpus

wrong_answer_msg = "Wrong answer for : {}/{}. \nGot:      {}\nExpected: {}\nMatcher: {}"
no_match_msg = "No match for: {}"


class dates_parser_test(unittest.TestCase):
    def test_expression_examples(self):
        from parse.date.functions import functions
        patterns_path = "parse/date/patterns.yaml"
        expressions_path = "parse/date/expressions.yaml"
        from reparse.builders import build_parser_from_yaml
        date_parser = build_parser_from_yaml(functions, expressions_path, patterns_path, with_name=True)

        for test_type, tests in corpus.iteritems():
            for test, answer in tests.iteritems():
                results, parser_name = date_parser(test)
                self.assertNotEqual(results, None, no_match_msg.format(test))
                self.assertTrue(any(results), no_match_msg.format(test))
                self.assertEqual(results, answer, wrong_answer_msg.format(test_type, test, results, answer, parser_name))