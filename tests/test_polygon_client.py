import unittest
from unittest.mock import patch, Mock


class TestPolygonClient(unittest.TestCase):
    def test_get_quote_calls_api(self):
        import os, sys, types
        os.environ.setdefault("POLYGON_API_KEY", "fake")
        # provide a fake requests module for environments without requests installed
        fake_requests = types.ModuleType("requests")
        # ensure a stub 'get' exists so patch.object can find it
        from unittest.mock import Mock as _M
        fake_requests.get = _M()
        sys.modules["requests"] = fake_requests
        import clients.polygon_client as pc
        with patch.object(pc.requests, "get") as mock_get:
            mock_resp = Mock()
            mock_resp.raise_for_status = Mock()
            mock_resp.json.return_value = {"results": []}
            mock_get.return_value = mock_resp

            res = pc.get_quote("AAPL")
            print("Api response:", res)
            self.assertIn("results", res)
            mock_get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
