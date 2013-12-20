#!python
from reparse.builders import build_from_yaml
from functions import functions


def percentage(part, whole):
    if whole == 0:
        return 0
    return round(100 * float(part) / float(whole))


class Dates:
    patterns = []

    def __init__(self, patterns_path="patterns.yaml", expressions_path="expressions.yaml"):
        self.patterns = build_from_yaml(functions, patterns_path, expressions_path)

    def evaluate(self):
        # Set up corpus and results
        from corpus import corpus

        results = {}
        for type in corpus:
            results[type] = 0
            # Run Patterns
        for type, tests in corpus.iteritems():
            print "---- {} ----".format(type)
            for test, answer in tests.iteritems():
                temp = results[type]
                for pattern in self.patterns:
                    #print "{} -> {}".format(test,pattern.findall(test))
                    if set(pattern.findall(test)) == set(answer): results[type] += 1
                if results[type] == temp:
                    print test

        # Print results
        final_results = []
        for type, value in corpus.iteritems():
            final_results.append(percentage(results[type], len(corpus[type])))
            print "{} - {}%".format(type, percentage(results[type], len(corpus[type])))
        return int(sum(final_results) / len(corpus))


if __name__ == "__main__":
    print "\nFinal Score: {}%".format(Dates().evaluate())
