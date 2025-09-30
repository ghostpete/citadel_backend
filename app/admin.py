from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.forms import TextInput, Textarea
from django import forms

class UserAdminConfig(UserAdmin):
    model = CustomUser
    search_fields = ("email", "first_name", "last_name")
    list_filter = ("is_staff", "is_active", "is_superuser")
    ordering = ("-date_joined",)
    list_display = ("email", "first_name", "last_name", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "account_id")}),
        ("Monetary Values", {"fields": ("user_funds", "free_margin", "balance", "equity", "margin_level")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "is_staff", "is_active")}
        ),
    )


# account_id = models.CharField(max_length=10, blank=True, null=True)

#     free_margin = models.DecimalField(verbose_name="Free Margin", max_digits=20, decimal_places=2, default=0.00, help_text="This is a monetary value.")
#     user_funds = models.DecimalField(verbose_name="User Funds", max_digits=20, decimal_places=2, default=0.00, help_text="This is a monetary value.")
#     balance = models.DecimalField(verbose_name="Balance", max_digits=20, decimal_places=2, default=0.00, help_text="This is a monetary value.")
#     equity = models.DecimalField(verbose_name="Equity", max_digits=20, decimal_places=2, default=0.00, help_text="This is a monetary value.")
#     margin_level = models.DecimalField(
#         help_text="The Margin Level is a Percentage value. It should range from 0% to 20%.", 
#         verbose_name="Margin Level",  max_digits=20, decimal_places=2,
#         default=0.00
#     )

admin.site.register(CustomUser, UserAdminConfig)