#!python
import unittest

class TestCat(unittest.TestCase):
    def test_run(self):
        from categorize import categorize_event
        self.assertEquals(categorize_event("Sample apple cherry wines"), "winery")

if __name__ == '__main__':
    unittest.main()
