import unittest
from utility import logger


class TestLoggerDecorator(unittest.TestCase):
    def test_exception_handler_logs_and_reraises(self):
        @logger.exception_handler(convert_exceptions=False)
        def f():
            raise RuntimeError("err")

        with self.assertRaises(RuntimeError):
            f()


if __name__ == "__main__":
    unittest.main()
