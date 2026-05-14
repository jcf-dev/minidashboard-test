from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from dashboard.models import Client, MonthlyTarget, Sale


class Command(BaseCommand):
    help = "Create demo clients, sales, and monthly targets."

    def handle(self, *args, **options):
        today = date.today()
        month_start = date(today.year, today.month, 1)

        clients = [
            (1, "Acme Supply Co.", "ops@acme.example"),
            (2, "Northwind Retail", "finance@northwind.example"),
        ]

        with transaction.atomic():
            for client_id, name, email in clients:
                self._ensure_demo_client(client_id, name, email)

            self._reset_client_id_sequence()

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

    def _reset_client_id_sequence(self):
        if connection.vendor != "postgresql":
            return

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT setval(
                    pg_get_serial_sequence('dashboard_client', 'id'),
                    COALESCE((SELECT MAX(id) FROM dashboard_client), 1),
                    true
                )
                """
            )

    def _ensure_demo_client(self, client_id, name, email):
        target = Client.objects.filter(id=client_id).first()
        duplicate = Client.objects.filter(email=email).exclude(id=client_id).first()

        if target is None:
            if duplicate is not None:
                duplicate.email = f"{email}.legacy-{duplicate.id}"
                duplicate.save(update_fields=["email"])

            target = Client.objects.create(id=client_id, name=name, email=email)
        elif duplicate is not None:
            self._merge_client_data(source=duplicate, target=target)
            duplicate.delete()

        target.name = name
        target.email = email
        target.save(update_fields=["name", "email"])
        return target

    def _merge_client_data(self, source, target):
        Sale.objects.filter(client=source).update(client=target)

        for monthly_target in MonthlyTarget.objects.filter(client=source):
            MonthlyTarget.objects.update_or_create(
                client=target,
                month=monthly_target.month,
                defaults={"goal": monthly_target.goal},
            )
