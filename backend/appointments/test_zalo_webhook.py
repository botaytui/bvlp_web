import hashlib
import json
import tempfile
from pathlib import Path
from django.test import RequestFactory, SimpleTestCase, override_settings
from .zalo_webhook import generate_signature, webhook


class ZaloWebhookTests(SimpleTestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.config = override_settings(ZALO_MINIAPP_API_KEY="test-key", ZALO_MINIAPP_ID="2927834622142925514", ZALO_MINIAPP_EVENT_DIR=self.directory.name)
        self.config.enable()
        self.addCleanup(self.config.disable)
        self.factory = RequestFactory()
        self.payload = {"event": "user.revoke.consent", "appId": "2927834622142925514", "userId": "private-user-test", "timestamp": 1234567890}

    def post(self, payload=None, signature=None):
        data = self.payload if payload is None else payload
        request = self.factory.post("/", data=json.dumps(data), content_type="application/json", HTTP_X_ZEVENT_SIGNATURE=generate_signature(data, "test-key") if signature is None else signature)
        return webhook(request)

    def test_official_signature_value_order(self):
        expected = hashlib.sha256(b"2927834622142925514user.revoke.consent1234567890private-user-testtest-key").hexdigest()
        self.assertEqual(generate_signature(self.payload, "test-key"), expected)

    def test_signed_duplicate_receipt_contains_no_user_id(self):
        self.assertEqual(self.post().status_code, 200)
        self.assertEqual(self.post().status_code, 200)
        files = list(Path(self.directory.name).glob("*.json"))
        self.assertEqual(len(files), 1)
        self.assertNotIn("private-user-test", files[0].read_text())

    def test_invalid_signature_creates_no_receipt(self):
        self.assertEqual(self.post(signature="wrong").status_code, 403)
        self.assertEqual(list(Path(self.directory.name).iterdir()), [])

    def test_other_app_rejected(self):
        self.assertEqual(self.post({**self.payload, "appId": "other"}).status_code, 403)

    def test_missing_identity_rejected(self):
        self.assertEqual(self.post({**self.payload, "userId": ""}).status_code, 400)

    @override_settings(ZALO_MINIAPP_API_KEY="")
    def test_unconfigured_fails_closed(self):
        self.assertEqual(self.post().status_code, 503)

    def test_bad_json_and_oversized_payload(self):
        for body, status in [(b"{", 400), (b"x" * 16385, 413)]:
            self.assertEqual(webhook(self.factory.post("/", data=body, content_type="application/json")).status_code, status)

    def test_health_and_method(self):
        self.assertEqual(webhook(self.factory.get("/")).status_code, 200)
        self.assertEqual(webhook(self.factory.put("/")).status_code, 405)
