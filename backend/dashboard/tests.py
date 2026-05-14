import json
from datetime import date
from decimal import Decimal

from django.core.management import call_command
from django.test import Client as HttpClient
from django.test import TestCase, override_settings

from .models import Client, MonthlyTarget, Sale


@override_settings(DASHBOARD_API_KEY="test-key")
class DashboardApiTests(TestCase):
    def setUp(self):
        self.http = HttpClient()
        self.client_record = Client.objects.create(
            name="Acme Supply Co.",
            email="ops@acme.example",
        )
        self.other_client = Client.objects.create(
            name="Northwind Retail",
            email="finance@northwind.example",
        )
        self.month = date.today().replace(day=1)
        MonthlyTarget.objects.create(
            client=self.client_record,
            month=self.month,
            goal=Decimal("10000.00"),
        )
        Sale.objects.create(
            client=self.client_record,
            label="Subscription",
            amount=Decimal("2500.00"),
            sold_at=self.month,
        )
        Sale.objects.create(
            client=self.other_client,
            label="Should not leak",
            amount=Decimal("9999.00"),
            sold_at=self.month,
        )

    def request(self, method="get", body=None, api_key="test-key"):
        kwargs = {
            "HTTP_X_API_KEY": api_key,
            "HTTP_X_CLIENT_ID": str(self.client_record.id),
        }
        if method == "patch":
            return self.http.patch(
                "/api/dashboard/",
                data=json.dumps(body or {}),
                content_type="application/json",
                **kwargs,
            )
        return self.http.get("/api/dashboard/", **kwargs)

    def test_requires_api_key(self):
        response = self.request(api_key="wrong-key")

        self.assertEqual(response.status_code, 401)

    def test_filters_sales_by_client_header(self):
        response = self.request()

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["client"]["id"], self.client_record.id)
        self.assertEqual(len(payload["sales"]), 1)
        self.assertEqual(payload["sales"][0]["label"], "Subscription")
        self.assertEqual(payload["monthlyGoal"], 10000.0)

    def test_patch_updates_monthly_goal(self):
        response = self.request("patch", {"monthlyGoal": 14500})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["monthlyGoal"], 14500.0)
        target = MonthlyTarget.objects.get(client=self.client_record, month=self.month)
        self.assertEqual(target.goal, Decimal("14500"))


class SeedDemoDataTests(TestCase):
    def test_seed_creates_client_expected_by_frontend(self):
        call_command("seed_demo_data", verbosity=0)

        self.assertTrue(
            Client.objects.filter(
                id=1,
                name="Acme Supply Co.",
                email="ops@acme.example",
            ).exists()
        )
        self.assertTrue(
            MonthlyTarget.objects.filter(
                client_id=1,
                month=date.today().replace(day=1),
            ).exists()
        )

    def test_seed_handles_existing_demo_client_with_different_id(self):
        Client.objects.create(id=10, name="Old Acme", email="ops@acme.example")

        call_command("seed_demo_data", verbosity=0)

        self.assertTrue(Client.objects.filter(id=1, email="ops@acme.example").exists())
