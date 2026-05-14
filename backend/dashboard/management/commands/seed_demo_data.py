from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand

from dashboard.models import Client, MonthlyTarget, Sale


class Command(BaseCommand):
    help = "Create demo clients, sales, and monthly targets."

    def handle(self, *args, **options):
        today = date.today()
        month_start = date(today.year, today.month, 1)

        clients = [
            ("Acme Supply Co.", "ops@acme.example"),
            ("Northwind Retail", "finance@northwind.example"),
        ]

        for name, email in clients:
            Client.objects.get_or_create(email=email, defaults={"name": name})

        acme = Client.objects.get(email="ops@acme.example")
        northwind = Client.objects.get(email="finance@northwind.example")

        MonthlyTarget.objects.update_or_create(
            client=acme,
            month=month_start,
            defaults={"goal": Decimal("18000.00")},
        )
        MonthlyTarget.objects.update_or_create(
            client=northwind,
            month=month_start,
            defaults={"goal": Decimal("12500.00")},
        )

        sales = [
            (acme, "Starter subscription", Decimal("3200.00"), month_start + timedelta(days=1)),
            (acme, "Expansion seats", Decimal("4900.00"), month_start + timedelta(days=5)),
            (acme, "Support package", Decimal("2750.00"), month_start + timedelta(days=11)),
            (acme, "Implementation", Decimal("6100.00"), month_start + timedelta(days=16)),
            (northwind, "Retail pilot", Decimal("2100.00"), month_start + timedelta(days=2)),
            (northwind, "Quarterly renewal", Decimal("4300.00"), month_start + timedelta(days=9)),
            (northwind, "Training", Decimal("1600.00"), month_start + timedelta(days=14)),
        ]

        for client, label, amount, sold_at in sales:
            Sale.objects.get_or_create(
                client=client,
                label=label,
                sold_at=sold_at,
                defaults={"amount": amount},
            )

        self.stdout.write(self.style.SUCCESS("Demo dashboard data is ready."))

