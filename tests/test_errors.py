import unittest
from utility import errors


class TestErrors(unittest.TestCase):
    def test_baseapp_error_dict(self):
        e = errors.BaseAppError("bad", code="E1")
        d = e.to_dict()
        self.assertIn("error", d)
        self.assertEqual(d["error"]["message"], "bad")
        self.assertEqual(d["error"]["code"], "E1")

    def test_wrap_exceptions_converts(self):
        @errors.wrap_exceptions
        def fn():
            raise ValueError("boom")

        with self.assertRaises(errors.ExternalServiceError):
            fn()


if __name__ == "__main__":
    unittest.main()
