test_output = []
tests_failed = []

def reset_tests():
    test_output = []

def get_results():
    return (test_output, tests_failed)

def test_print(str):
    test_output.append(str)

def test_assert(expected, result):
    if expected == result:
        msg = "pass: '%s'" % (expected)
        test_print(msg)
        return
    msg = "FAIL: expected\n  '%s'\nbut got\n  '%s'" % (expected, result)
    test_print(msg)
    tests_failed.append(msg)

def test_report_results(callback):
    results = ''
    all_passed = len(tests_failed) == 0
    if all_passed:
        results += 'All tests passed\n'
    else:
        results += 'SOME TESTS FAILED\n'

    results += '\n'.join(test_output)

    if all_passed:
        results += '\n\nAll tests passed\n'
    else:
        results += '\n\nSOME TESTS FAILED\n'
        results += 'Failing tests:\n'
        results += '\n'.join(tests_failed)
        results += '\n'

    callback(results)
