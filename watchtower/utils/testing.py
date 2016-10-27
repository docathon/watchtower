import unittest

__all__ = ["assert_equal", "assert_not_equal", "assert_true",
           "assert_false", "assert_raises"]

_dummy = unittest.TestCase('__init__')
assert_equal = _dummy.assertEqual
assert_not_equal = _dummy.assertNotEqual
assert_true = _dummy.assertTrue
assert_false = _dummy.assertFalse
assert_raises = _dummy.assertRaises
