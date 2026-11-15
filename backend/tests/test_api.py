"""Regressoes da API com banco simulado; nao requer dumps nem credenciais."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from backend.api import app as api


class ApiTests(unittest.TestCase):
    def setUp(self):
        api.app.config.update(TESTING=True, DEV_RELOAD=False)
        api._CACHE.clear()
        self.client = api.app.test_client()

    def test_frontend_loads_without_development_script(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b"/__dev_timestamp", response.data)

    def test_private_project_files_are_not_served(self):
        for url in ("/.env", "/.git", "/backend/api/app.py", "/database/scripts/database.sql", "/README.md"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_html_traversal_cannot_read_outside_frontend(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            public = root / "frontend"
            public.mkdir()
            (root / "private.html").write_text("private-data", encoding="utf-8")
            with patch.object(api, "DIRETORIO_FRONTEND", str(public)):
                response = self.client.get("/../private.html")
                self.assertEqual(response.status_code, 404)
                self.assertNotIn(b"private-data", response.data)

    def test_filtered_list_is_cached_after_first_query(self):
        with patch.object(api, "_query_all", return_value=[{"numero_ficha": 7}]) as query:
            first = self.client.get("/api/fichas?search=demo")
            second = self.client.get("/api/fichas?search=demo")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.headers["X-Data-Cache"], "MISS")
        self.assertEqual(second.headers["X-Data-Cache"], "HIT")
        self.assertEqual(first.json[0]["id"], 7)
        query.assert_called_once()

    def test_detail_is_cached_after_first_query(self):
        with patch.object(api, "_query_one", return_value={"numero_ficha": 7}) as query:
            first = self.client.get("/api/ficha/7")
            second = self.client.get("/api/ficha/7")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.headers["X-Data-Cache"], "HIT")
        self.assertEqual(second.json["id"], 7)
        query.assert_called_once()

    def test_expired_cache_is_not_returned(self):
        with patch.object(api.time, "monotonic", return_value=10):
            api._cache_set("item", [1], 2)
        with patch.object(api.time, "monotonic", return_value=13):
            self.assertIsNone(api._cache_get("item"))

    def test_write_endpoints_remain_disabled(self):
        for method, path in (("post", "/api/fichas"), ("put", "/api/ficha/7"), ("delete", "/api/ficha/7")):
            self.assertEqual(getattr(self.client, method)(path).status_code, 405)

    def test_development_endpoint_is_disabled_by_default(self):
        self.assertEqual(self.client.get("/__dev_timestamp").status_code, 404)

    def test_unconfigured_cross_origin_request_is_not_allowed(self):
        response = self.client.get("/", headers={"Origin": "https://unrelated.example"})
        self.assertNotIn("Access-Control-Allow-Origin", response.headers)


if __name__ == "__main__":
    unittest.main()
