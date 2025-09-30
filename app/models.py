import random

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token



class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a user with an email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)

    account_id = models.CharField(max_length=10, blank=True, null=True)

    free_margin = models.DecimalField(verbose_name="Free Margin", max_digits=20, decimal_places=2, default=0.00, help_text="This is a monetary value.")
    user_funds = models.DecimalField(verbose_name="User Funds", max_digits=20, decimal_places=2, default=0.00, help_text="This is a monetary value.")
    balance = models.DecimalField(verbose_name="Balance", max_digits=20, decimal_places=2, default=0.00, help_text="This is a monetary value.")
    equity = models.DecimalField(verbose_name="Equity", max_digits=20, decimal_places=2, default=0.00, help_text="This is a monetary value.")
    margin_level = models.DecimalField(
        help_text="The Margin Level is a Percentage value. It should range from 0% to 20%. Do not add the '%' symbol", 
        verbose_name="Margin Level",  max_digits=20, decimal_places=2,
        default=0.00
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []  # Email & Password are required by default
    
    class Meta:
        verbose_name_plural = "Users"
        verbose_name = "User"

    def __str__(self):
        return self.email


def generate_unique_account_id():
    while True:
        account_id = str(random.randint(10**9, 10**10 - 1))  # 10-digit number
        if not CustomUser.objects.filter(account_id=account_id).exists():
            return account_id

# Signal: auto-create token for each new user
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

        # Assign unique 10-digit account_id if not already set
        if not instance.account_id:
            instance.account_id = generate_unique_account_id()
            instance.save(update_fields=["account_id"])




class Trader(models.Model):
    name = models.CharField(max_length=150)
    country = models.CharField(max_length=100)
    avatar = models.URLField(max_length=255, blank=True, null=True)
    gain = models.DecimalField(max_digits=10, decimal_places=2)  # e.g. 194.32
    risk = models.PositiveSmallIntegerField()  # assuming 1–10 risk score
    capital = models.CharField(max_length=50)  # stored as string because of "$"
    copiers = models.PositiveIntegerField()
    avg_trade_time = models.CharField(max_length=50)  # e.g. "1 week"
    trades = models.PositiveIntegerField()

    created_at = models.DateTimeField(auto_now_add=True)  # optional
    updated_at = models.DateTimeField(auto_now=True)      # optional

    def __str__(self):
        return f"{self.name} ({self.country})"
    
    class Meta:
        verbose_name_plural = "Traders"
        verbose_name = "Trader"

class Transaction(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("successful", "Successful"),
        ("failed", "Failed"),
    ]

    TRANSACTION_TYPES = [
        ("deposit", "Deposit"),
        ("withdrawal", "Withdrawal"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions"
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    reference = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} - {self.transaction_type} - {self.amount} ({self.status})"


class Ticket(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    subject = models.CharField(max_length=200, blank=True, null=False)
    category = models.CharField(max_length=200, blank=True, null=False)
    description = models.TextField(blank=True, null=False)

    def __str__(self):
        return self.subject
    











