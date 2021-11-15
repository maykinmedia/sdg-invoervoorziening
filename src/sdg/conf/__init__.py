def load_tests(*args):
    """
    Do not load tests from the conf/ dir.
    see https://docs.python.org/3.7/library/unittest.html#load-tests-protocol
    """
    return None
