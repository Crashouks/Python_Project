import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tourist_routes.api import security  # noqa: E402

HAS_API_STACK = all(
    importlib.util.find_spec(name) for name in ("fastapi", "sqlalchemy", "httpx", "multipart")
)

HIKE = {
    "type": "HikingRoute",
    "name": "Карпатська мандрівка",
    "country": "Україна",
    "start_city": "Ворохта",
    "length_km": 45,
    "description": "Триденний похід через полонини.",
    "ratings": [9, 10, 8],
    "difficulty": "середній",
    "elevation_gain_m": 1800,
}


class SecurityTests(unittest.TestCase):
    def test_password_hash_roundtrip(self):
        stored = security.hash_password("secret123")
        self.assertNotIn("secret123", stored)
        self.assertTrue(security.verify_password("secret123", stored))
        self.assertFalse(security.verify_password("wrong", stored))
        self.assertFalse(security.verify_password("secret123", "broken-hash"))

    def test_token_roundtrip(self):
        token = security.create_access_token("traveler")
        self.assertEqual(security.decode_access_token(token), "traveler")

    def test_invalid_and_expired_tokens_rejected(self):
        self.assertIsNone(security.decode_access_token("not-a-token"))
        expired = security.create_access_token("traveler", expires_minutes=-1)
        self.assertIsNone(security.decode_access_token(expired))


@unittest.skipUnless(HAS_API_STACK, "потрібні fastapi, sqlalchemy, httpx, python-multipart")
class ApiTests(unittest.TestCase):
    def setUp(self):
        from fastapi.testclient import TestClient
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from sqlalchemy.pool import StaticPool

        from tourist_routes.api.database import Base, get_db
        from tourist_routes.api.main import app

        engine = create_engine(
            "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
        )
        Base.metadata.create_all(bind=engine)
        Session = sessionmaker(bind=engine, autoflush=False)

        def override_get_db():
            db = Session()
            try:
                yield db
            finally:
                db.close()

        app.dependency_overrides[get_db] = override_get_db
        self.app = app
        self.client = TestClient(app)

    def tearDown(self):
        self.app.dependency_overrides.clear()

    def auth_headers(self, username="traveler", password="secret123"):
        self.client.post("/auth/register", json={"username": username, "password": password})
        response = self.client.post(
            "/auth/login", data={"username": username, "password": password}
        )
        self.assertEqual(response.status_code, 200)
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())

    def test_register_duplicate_and_bad_login(self):
        body = {"username": "traveler", "password": "secret123"}
        self.assertEqual(self.client.post("/auth/register", json=body).status_code, 201)
        self.assertEqual(self.client.post("/auth/register", json=body).status_code, 409)
        bad = self.client.post("/auth/login", data={"username": "traveler", "password": "x"})
        self.assertEqual(bad.status_code, 401)

    def test_protected_endpoints_require_token(self):
        self.assertEqual(self.client.post("/routes", json=HIKE).status_code, 401)
        self.assertEqual(self.client.put("/routes/1", json=HIKE).status_code, 401)
        self.assertEqual(self.client.delete("/routes/1").status_code, 401)
        self.assertEqual(self.client.get("/auth/me").status_code, 401)
        bad = {"Authorization": "Bearer garbage"}
        self.assertEqual(self.client.post("/routes", json=HIKE, headers=bad).status_code, 401)

    def test_crud_flow(self):
        headers = self.auth_headers()
        created = self.client.post("/routes", json=HIKE, headers=headers)
        self.assertEqual(created.status_code, 201)
        route = created.json()
        self.assertEqual(route["average_rating"], 9.0)
        self.assertAlmostEqual(route["estimated_duration_hours"], 45 / 4 + 1800 / 600, places=2)

        self.assertEqual(self.client.get(f"/routes/{route['id']}").status_code, 200)
        self.assertEqual(len(self.client.get("/routes").json()), 1)

        updated = dict(HIKE, name="Нова назва", length_km=50)
        response = self.client.put(f"/routes/{route['id']}", json=updated, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["name"], "Нова назва")

        self.assertEqual(
            self.client.delete(f"/routes/{route['id']}", headers=headers).status_code, 204
        )
        self.assertEqual(self.client.get(f"/routes/{route['id']}").status_code, 404)

    def test_not_found(self):
        headers = self.auth_headers()
        self.assertEqual(self.client.get("/routes/999").status_code, 404)
        self.assertEqual(self.client.put("/routes/999", json=HIKE, headers=headers).status_code, 404)
        self.assertEqual(self.client.delete("/routes/999", headers=headers).status_code, 404)

    def test_validation_errors_422(self):
        headers = self.auth_headers()
        cases = [
            dict(HIKE, length_km=-5),
            dict(HIKE, ratings=[11]),
            dict(HIKE, type="Unknown"),
            {k: v for k, v in HIKE.items() if k != "difficulty"},
            dict(HIKE, name="   "),
        ]
        for body in cases:
            response = self.client.post("/routes", json=body, headers=headers)
            self.assertEqual(response.status_code, 422, body)

    def test_filtering(self):
        headers = self.auth_headers()
        bus = {
            "type": "BusTour", "name": "Тур довкола Монблану", "country": "Франція",
            "start_city": "Шамоні", "length_km": 170, "description": "Кільцевий тур.",
            "ratings": [9], "stops_count": 8,
        }
        for body in (HIKE, bus):
            self.client.post("/routes", json=body, headers=headers)
        by_name = self.client.get("/routes", params={"name": "карпат"}).json()
        self.assertEqual([r["country"] for r in by_name], ["Україна"])
        by_type = self.client.get("/routes", params={"type": "BusTour"}).json()
        self.assertEqual(len(by_type), 1)
        long_ones = self.client.get("/routes", params={"min_length_km": 100}).json()
        self.assertEqual([r["type"] for r in long_ones], ["BusTour"])

    def test_cors_headers(self):
        response = self.client.options(
            "/routes",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
            },
        )
        self.assertEqual(response.headers.get("access-control-allow-origin"), "http://localhost:3000")


if __name__ == "__main__":
    unittest.main()
