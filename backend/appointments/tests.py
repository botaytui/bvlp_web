import json
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import AppointmentRequest, Specialty


class AppointmentApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.specialty, _ = Specialty.objects.get_or_create(
            code="ho-hap", defaults={"name": "Khám hô hấp"}
        )

    def payload(self, **overrides):
        data = {
            "fullName": "Nguyễn Văn An",
            "phone": "0912 345 678",
            "appointmentDate": str(timezone.localdate() + timedelta(days=1)),
            "specialty": "ho-hap",
            "symptoms": "Ho và sốt dai dẳng 3 ngày",
            "consent": True,
            "idempotencyKey": "test-request-1",
        }
        data.update(overrides)
        return data

    def post(self, payload):
        return self.client.post(
            reverse("create-appointment"),
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_health(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_create_appointment(self):
        response = self.post(self.payload())
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()["success"])
        self.assertEqual(AppointmentRequest.objects.count(), 1)
        self.assertEqual(AppointmentRequest.objects.get().phone_normalized, "0912345678")
        self.assertEqual(AppointmentRequest.objects.get().symptoms, "Ho và sốt dai dẳng 3 ngày")

    def test_create_without_specialty_when_symptoms_are_provided(self):
        response = self.post(self.payload(
            specialty="",
            symptoms="Khó thở khi vận động",
            idempotencyKey="test-no-specialty",
        ))
        self.assertEqual(response.status_code, 201)
        appointment = AppointmentRequest.objects.get()
        self.assertIsNone(appointment.specialty)
        self.assertEqual(appointment.symptoms, "Khó thở khi vận động")

    def test_requires_specialty_or_symptoms(self):
        response = self.post(self.payload(specialty="", symptoms=""))
        self.assertEqual(response.status_code, 400)
        self.assertIn("specialty", response.json()["errors"])
        self.assertIn("symptoms", response.json()["errors"])

    def test_idempotency_returns_existing_appointment(self):
        first = self.post(self.payload()).json()
        second_response = self.post(self.payload())
        self.assertEqual(second_response.status_code, 200)
        self.assertTrue(second_response.json()["duplicate"])
        self.assertEqual(second_response.json()["bookingCode"], first["bookingCode"])
        self.assertEqual(AppointmentRequest.objects.count(), 1)

    def test_rejects_missing_consent(self):
        response = self.post(self.payload(consent=False))
        self.assertEqual(response.status_code, 400)
        self.assertIn("consent", response.json()["errors"])

    def test_rejects_past_date(self):
        response = self.post(
            self.payload(appointmentDate=str(timezone.localdate() - timedelta(days=1)))
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("appointmentDate", response.json()["errors"])

    def test_honeypot_rejects_bot(self):
        response = self.post(self.payload(website="spam"))
        self.assertEqual(response.status_code, 400)
