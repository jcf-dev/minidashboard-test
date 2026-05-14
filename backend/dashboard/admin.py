from django.contrib import admin

from .models import Client, MonthlyTarget, Sale


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("label", "client", "amount", "sold_at")
    list_filter = ("client", "sold_at")
    search_fields = ("label", "client__name")


@admin.register(MonthlyTarget)
class MonthlyTargetAdmin(admin.ModelAdmin):
    list_display = ("client", "month", "goal", "updated_at")
    list_filter = ("month", "client")

