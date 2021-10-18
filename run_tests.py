# subset of tests outside of Anki

import verbs
import test_util

def test():
    print("Running subset of tests that work outside Anki")
    verbs.test(test_util)

test()
