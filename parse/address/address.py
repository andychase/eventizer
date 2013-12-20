"""
Uses Regex through the ExpressionPattern engine to find addresses
embedded in text and parse them.
"""
from functions import functions

__name__ = "Address"
import sys

sys.path.append('.')
from reparse.builders import build_from_yaml


class Address():
    patterns = []

    def __init__(self, patterns_path="parse/address/patterns.yaml", expressions_path="parse/address/expressions.yaml"):
        self.patterns = build_from_yaml(functions, expressions_path, patterns_path)

    def parse(self, line):
        patterns = self.patterns
        output = []
        for pattern in patterns:
            results = pattern.findall(line)
            if results and any(results):
                for result in results:
                    output.append(result)
        return output
