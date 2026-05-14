from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Sale(models.Model):
    client = models.ForeignKey(Client, related_name="sales", on_delete=models.CASCADE)
    label = models.CharField(max_length=160)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    sold_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-sold_at", "-id"]

    def __str__(self):
        return f"{self.label} - {self.client.name}"


class MonthlyTarget(models.Model):
    client = models.ForeignKey(
        Client,
        related_name="monthly_targets",
        on_delete=models.CASCADE,
    )
    month = models.DateField(help_text="Use the first day of the target month.")
    goal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["client", "month"],
                name="unique_monthly_target_per_client",
            )
        ]
        ordering = ["-month"]

    def __str__(self):
        return f"{self.client.name} target for {self.month:%Y-%m}"

