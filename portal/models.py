from datetime import timedelta, datetime, date

import decimal
from math import remainder
from operator import is_
import random
import re
from click import DateTime
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import string
from django.utils import timezone
from django.core.cache import cache
from django.db import transaction

review_enums = {
    "pending": "pending",
    "approved": "approved",
    "denied": "denied",
}


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, default=0.0
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True, default=0.0
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CitySection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=70)
    density = models.CharField(
        max_length=50,
        choices=[
            ("low", "low"),
            ("medium", "medium"),
            ("high", "high"),
            ("cbd", "cbd"),
        ],
    )

    def __str__(self):
        return self.name + " - " + self.city.name


class Account(models.Model):

    def create_acc_num(self):
        while True:
            acc_num = f"{random.randint(100, 999)}-{random.randint(1000, 9999)}-{random.randint(10, 99)}"
            if not Account.objects.filter(account_number=acc_num).exists():
                return acc_num

    account_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(
        "User",
        on_delete=models.DO_NOTHING,
        db_index=True,
        null=True,
        related_name="accounts",
    )
    property = models.ForeignKey(
        "Property", on_delete=models.DO_NOTHING, null=True, related_name="accounts"
    )
    water_meter_number = models.CharField(
        unique=True, max_length=20, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def generate_meter_num(self):
        values = string.digits
        num = "".join(random.choice(values) for _ in range(10))

        first_val = self.property.community.name[0]
        return first_val.upper() + num + "25"

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.create_acc_num()
        if not self.water_meter_number:
            self.water_meter_number = self.generate_meter_num()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.account_number}"


class User(AbstractUser):
    is_active = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, unique=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)

    @property
    def primary_account(self):
        """Get user's primary account if any"""
        return self.accounts.first()

    def get_accounts_for_property(self, property_id):
        """Get all accounts associated with a specific property"""
        return self.accounts.filter(property_id=property_id)

    @property
    def primary_account(self):
        cache_key = f"user_{self.id}_primary_account"
        account = cache.get(cache_key)
        if not account:
            account = self.accounts.first()
            cache.set(cache_key, account, timeout=3600)
        return account

    def __str__(self):
        return self.username


class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(
                minutes=5
            )  # Code expires in 5 minutes
        super().save(*args, **kwargs)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.username} - {self.code}"


class Property(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="properties")
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    community = models.ForeignKey(CitySection, on_delete=models.CASCADE)
    area_sq_m = models.FloatField()
    address = models.TextField()
    value = models.FloatField()
    property_type = models.CharField(
        max_length=50,
        choices=[
            ("residential", "residential"),
            ("commercial", "commercial"),
            ("industrial", "industrial"),
            ("agricultural", "agricultural"),
            ("institutional", "institutional"),
            ("vacant", "vacant"),
            ("other", "other"),
        ],
        null=True,
    )
    housing_status = models.CharField(
        max_length=50, choices=[("owned", "owned"), ("rented", "rented")]
    )
    tax = models.ForeignKey("Tax", on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address + " - " + self.owner.username + "(" + self.city.name + ")"


### W A T E R ###


class BillingDetails(models.Model):
    last_receipt_date = models.DateField(null=True, blank=True)
    bill_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):
        """Override save to set default values for last_receipt_date and due_date."""
        if not self.last_receipt_date:
            previous_period = BillingDetails.objects.order_by("-bill_date").first()
            self.last_receipt_date = (
                previous_period.last_receipt_date if previous_period else date.today()
            )

        if not self.due_date:
            self.due_date = self.last_receipt_date + timedelta(days=30)

        super().save(*args, **kwargs)


class WaterUsage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    previous_reading = models.FloatField(null=True, blank=True)
    current_reading = models.FloatField(null=True, blank=True)
    consumption = models.FloatField(null=True, blank=True)
    date_recorded = models.DateTimeField(auto_now_add=True)

    def calculate_consumption(self):
        if self.current_reading <= self.previous_reading:
            raise ValueError("Current reading must be greater than previous reading.")
        if self.current_reading is not None and self.previous_reading is not None:
            return self.current_reading - self.previous_reading
        else:
            return 0

    def save(self, *args, **kwargs):
        """Override save to calculate consumption."""
        if not self.consumption:
            self.consumption = self.calculate_consumption()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Water Usage: {self.consumption} m³ on {self.date_recorded.strftime('%Y-%m-%d %H:%M:%S')}"


class Charges(models.Model):
    rates = models.FloatField(default=0.00)
    water_charges = models.FloatField(default=0.00)
    sewerage = models.FloatField(default=0.00)
    street_lighting = models.FloatField(default=0.00)
    roads_charge = models.FloatField(default=0.00)
    education_levy = models.FloatField(default=0.00)
    total_due = models.FloatField(default=0.00)

    def get_total_due(self):
        return sum(
            [
                self.rates,
                self.water_charges,
                self.sewerage,
                self.street_lighting,
                self.roads_charge,
                self.education_levy,
            ]
        )

    def calculate_water_charges(self, consumption=0):
        """Calculate water charges based on usage."""
        base_rate = 4.66 / 6  # Base rate per cubic meter

        if consumption <= 0:
            return 0.00
        elif consumption <= 10:  # First 10 cubic meters
            return consumption * base_rate
        elif consumption <= 20:  # 11-20 cubic meters
            return (10 * base_rate) + ((consumption - 10) * (base_rate * 1.2))
        else:  # Above 20 cubic meters
            return (
                (10 * base_rate)
                + (10 * (base_rate * 1.2))
                + ((consumption - 20) * (base_rate * 1.5))
            )

    @property
    def all_positive_charges(self):
        return all(
            value > 0
            for value in [
                self.rates,
                self.water_charges,
                self.sewerage,
                self.street_lighting,
                self.roads_charge,
                self.education_levy,
            ]
        )

    def save(self, *args, **kwargs):
        """Override save to calculate total due."""
        self.total_due = self.get_total_due()
        super().save(*args, **kwargs)


class WaterDebt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    over_90_days = models.FloatField(null=True, blank=True, default=0.00)
    over_60_days = models.FloatField(null=True, blank=True, default=0.00)
    over_30_days = models.FloatField(null=True, blank=True, default=0.00)
    total_debt = models.FloatField(null=True, blank=True, default=0.00)

    def calculate_total_debt(self):
        """Calculate the total debt."""
        return self.over_90_days + self.over_60_days + self.over_30_days

    def save(self, *args, **kwargs):
        """Override save to calculate total debt."""
        if not self.total_debt:
            self.total_debt = self.calculate_total_debt()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Water Debt: {self.total_debt} on {timezone.now().strftime('%Y-%m-%d %H:%M:%S')}"


class WaterBill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="water_bills",
    )
    account = models.ForeignKey(
        Account,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="water_bills",
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="water_bills",
    )
    bill_number = models.CharField(max_length=10, unique=True, blank=True, null=True)
    billing_period = models.OneToOneField(
        BillingDetails,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="billing_period",
    )
    water_usage = models.OneToOneField(
        WaterUsage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="water_usage",
    )
    charges = models.OneToOneField(Charges, on_delete=models.CASCADE, null=True)
    water_debt = models.OneToOneField(
        WaterDebt,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="water_debt",
    )
    credit = models.FloatField(null=True, blank=True, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.FloatField(default=0.00)
    amount_paid = models.FloatField(default=0.00)
    remaining_balance = models.FloatField(default=0.00)
    payment_status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "pending"),
            ("paid", "paid"),
            ("overdue", "overdue"),
        ],
        default="pending",
    )

    def get_remaining_balance(self):
        """Calculate the remaining balance after payment."""

        return max(self.total_amount - self.amount_paid, 0)

    def update_payment_status(self):
        """Determine the payment status based on the remaining balance."""
        if self.remaining_balance > 0:
            self.payment_status = "pending"
        elif self.remaining_balance == 0:
            self.payment_status = "paid"
        elif self.billing_period and timezone.now() > self.billing_period.due_date:
            self.payment_status = "overdue"
        else:
            self.payment_status = "pending"

    def create_bill_number(self):
        return str(uuid.uuid4())[:10].upper()

    def calculate_total(self):
        """Calculate total bill amount including charges and debt."""
        charges_total = self.charges.total_due if self.charges else 0
        debt_total = self.water_debt.total_debt if self.water_debt else 0
        return charges_total + debt_total - (self.credit or 0)

    def calculate_water_charges(self):
        """Calculate charges based on water usage and other factors."""
        if self.water_usage and self.charges:
            self.charges.water_charges = self.charges.calculate_water_charges(
                consumption=self.water_usage.consumption
            )
            self.charges.total_due = self.charges.get_total_due()
            self.charges.save()

    @classmethod
    def create_bill(cls, readings_data, user=None, account=None):
        """
        Create a water bill from readings dictionary.

        Args:
            readings_data: dict with previous_reading and current_reading
            user: User instance
            account: Account instance
        """
        with transaction.atomic():
            water_usage = WaterUsage.objects.create(
                previous_reading=readings_data["previous_reading"],
                current_reading=readings_data["current_reading"],
            )

            charges = Charges.objects.create()

            bill = cls.objects.create(
                user=user, account=account, water_usage=water_usage, charges=charges
            )

            bill.calculate_water_charges()
            bill.total_amount = bill.calculate_total()
            bill.remaining_balance = bill.get_remaining_balance()
            bill.update_payment_status()
            bill.save()

            return bill

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total()
        self.remaining_balance = self.get_remaining_balance()
        self.update_payment_status()

        if not self.bill_number:
            self.bill_number = self.create_bill_number()

        if self.user != self.account.user:
            raise ValueError("User and account owner must be the same.")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill #{self.bill_number} - {self.city.name if self.city else 'N/A'}"

class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    city_registered = models.ForeignKey("City", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(
        max_length=50,
        choices=[
            ("individual", "Individual"),
            ("corporate", "Corporate"),
            ("partnership", "Partnership"),
            ("joint_venture", "Joint Venture"),
            ("limited_liability_company", "Limited Liability Company"),
        ],
    )
    purpose = models.TextField(null=True)
    reg_num = models.CharField(
        max_length=100, unique=True, blank=True
    )  # Remove default
    tax = models.ForeignKey("Tax", on_delete=models.CASCADE, null=True)
    address = models.TextField(null=True)

    status = models.CharField(
        max_length=50,
        choices=[
            ("closed", "Closed"),
            ("active", "Active"),
            ("suspended", "Suspended"),
        ],
        null=True,
        default="active",
    )

    def generate_registration_number(self):
        """Generates a unique business registration number."""
        values = string.digits
        num = "".join(random.choice(values) for _ in range(10))

        types = {
            "individual": "I-",
            "corporate": "C-",
            "partnership": "P-",
            "joint_venture": "J-",
            "limited_liability_company": "L-",
        }
        return (
            types.get(self.type, "U-") + num + "25"
        )  # "U-" as fallback if type is invalid

    def save(self, *args, **kwargs):
        """Auto-generate a reg_num if it is not set."""
        if not self.reg_num:
            self.reg_num = self.generate_registration_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.city_registered.name}"


class BusinessLicense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(
        "Business", on_delete=models.DO_NOTHING, related_name="licenses"
    )

    LICENSE_TYPES = [
        ("business_permit", "Business Permit"),
        ("business_registration", "Business Registration"),
        ("sign_permit", "Sign Permit"),
        ("liquor_license", "Liquor License"),
        ("food_permit", "Food Permit"),
        ("tax_permit", "Tax Permit"),
        ("fire_permit", "Fire Permit"),
        ("health_permit", "Health Permit"),
        ("public_health_permit", "Public Health Permit"),
    ]

    type = models.CharField(max_length=50, choices=LICENSE_TYPES, null=False)
    issue_date = models.DateTimeField(default=timezone.now)
    expiration_date = models.DateTimeField(null=True, blank=True)
    duration_months = models.IntegerField(null=False, default=12)  # Default to 1 year
    license_fee = models.DecimalField(
        max_digits=10, decimal_places=2, null=False, blank=True, default=0
    )

    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
    ]

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="active")
    approval_status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "pending"),
            ("approved", "approved"),
            ("denied", "denied"),
        ],
        default="pending",
    )

    LICENSE_PRICING = {
        "business_permit": 41.67,  # Base price per month
        "business_registration": 160,
        "sign_permit": 30.00,
        "liquor_license": 100.00,
        "food_permit": 70.00,
        "tax_permit": 70.00,
        "fire_permit": 45.00,
        "health_permit": 55.00,
        "public_health_permit": 65.00,
    }

    def calculate_expiration_date(self):
        """Calculate expiration date based on issue_date + duration_months"""
        if self.issue_date is None:
            return None
        return self.issue_date + timedelta(days=self.duration_months * 30)

    def calculate_fee(self):
        """Calculate license fee based on type and duration"""
        base_price = self.LICENSE_PRICING.get(self.type, 50.00)  # Default base price
        return base_price * self.duration_months

    def save(self, *args, **kwargs):
        """Override save to automatically set expiration date and fee"""
        if not self.expiration_date:
            self.expiration_date = self.calculate_expiration_date()
        if not self.license_fee:
            self.license_fee = self.calculate_fee()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.business.name} - {self.type} ({self.duration_months} months)"


class BusinessLicenseApproval(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    license = models.OneToOneField(
        BusinessLicense, on_delete=models.CASCADE, null=False
    )
    admin = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    review_status = models.CharField(
        max_length=50,
        choices=review_enums.items(),
        default="pending",
        null=False,
    )

    review_date = models.DateTimeField(auto_now_add=True)
    rejection_reason = models.TextField(null=True)


class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    plate_number = models.CharField(max_length=20, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    city_registered = models.ForeignKey(City, on_delete=models.DO_NOTHING, null=True)
    brand = models.CharField(max_length=50, null=True)
    model = models.CharField(max_length=50, null=True)
    color = models.CharField(max_length=50, null=True)
    image = models.ImageField(upload_to="vehicle_images/", null=True, blank=True)
    vehicle_type = models.CharField(
        max_length=50,
        choices=[
            ("car", "car"),
            ("motorcycle", "motorcycle"),
            ("truck", "truck"),
            ("bus", "bus"),
            ("other", "other"),
        ],
        null=True,
    )
    tax = models.ForeignKey("Tax", on_delete=models.CASCADE, null=True)
    document = models.FileField(upload_to="vehicle_documents/", null=True, blank=True)
    approval_status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "pending"),
            ("approved", "approved"),
            ("denied", "denied"),
        ],
        default="pending",
    )
    is_active = models.BooleanField(default=False)
    registered_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Ensures only one vehicle can be active per user at a time."""
        if self.is_active:
            # Set all other vehicles of this user to inactive
            Vehicle.objects.filter(owner=self.owner).exclude(id=self.id).update(
                is_active=False
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.plate_number + " - " + self.owner.username


class VehicleApproval(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.OneToOneField(Vehicle, on_delete=models.CASCADE, null=False)
    admin = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    review_status = models.CharField(
        max_length=50,
        choices=review_enums.items(),
        default="pending",
        null=False,
    )

    review_date = models.DateTimeField(auto_now_add=True)
    rejection_reason = models.TextField(null=True)

    def __str__(self):
        return self.vehicle.vehicle_plate_number + " - " + self.review_status


class ParkingTicket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="parking_tickets"
    )
    city = models.ForeignKey(
        City, on_delete=models.DO_NOTHING, related_name="parking_tickets", null=True
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    minutes_issued = models.IntegerField(null=False, default=0)
    expiry_at = models.DateTimeField(null=True, blank=True, editable=False)
    amount = models.FloatField(null=False, default=0)

    STATUS_CHOICES = [
        ("active", "Active"),
        ("expired", "Expired"),
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="active")

    def create_ticket_number(self):
        """Generate a unique ticket number."""
        while True:
            ticket_number = f"{random.randint(1000, 9999)}-{random.randint(1000, 9999)}"
            if not ParkingTicket.objects.filter(ticket_number=ticket_number).exists():
                return ticket_number

    def calculate_expiry(self):
        """Calculate the expiry time based on issued_at and minutes_issued."""
   

        if self.issued_at is None:
            raise ValueError("issued_at cannot be None when calculating expiry.")
        return self.issued_at + timedelta(minutes=self.minutes_issued)

    def calculate_amount(self):
        """Calculate the amount based on minutes issued."""
        return self.minutes_issued / 60  # $1 for every 60 minutes

    def update_status(self):
        """Automatically update the status based on expiry time."""
        now = timezone.now()
        if self.expiry_at and now >= self.expiry_at:
            self.status = "expired"

    def save(self, *args, **kwargs):
        if self.issued_at is None:
             self.issued_at = timezone.now()
    
        """Ensure correct values are set before saving."""
        if not self.expiry_at:  # Set expiry only if not already set
            self.expiry_at = self.calculate_expiry()

        if not self.ticket_number:
            self.ticket_number = self.create_ticket_number()

        self.amount = self.calculate_amount()  # Calculate amount before saving

        self.update_status()  # Update status before saving

        # Ensure only one active ticket per user
        if self.status == "active":
            ParkingTicket.objects.filter(user=self.user, status="active").exclude(id=self.id).update(status="expired")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle.plate_number} - {self.issued_at.strftime('%Y-%m-%d %H:%M:%S')}"


class ParkingTicketBundle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ticket_bundles")
    purchased_at = models.DateTimeField(auto_now_add=True)
    quantity = models.PositiveIntegerField(default=0)  # number of prepaid tickets
    ticket_minutes = models.PositiveIntegerField(default=60)  # each ticket's value
    price_paid = models.FloatField(default=0.0)  # total price with discount
    tickets_redeemed = models.PositiveIntegerField(default=0)

    def has_available_tickets(self):
        return self.tickets_redeemed < self.quantity

    def redeem_ticket(self):
        if not self.has_available_tickets():
            raise Exception("No more prepaid tickets available")
        self.tickets_redeemed += 1
        self.save()

    def remaining_tickets(self):
        return self.quantity - self.tickets_redeemed

    def __str__(self):
        return f"{self.user.username} - {self.remaining_tickets()} remaining"


class IssueReport(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    category = models.CharField(
        max_length=50,
        choices=[
            ("water", "water"),
            ("electricity", "electricity"),
            ("sewer", "sewer"),
            ("garbage", "garbage"),
            ("road", "road"),
            ("other", "other"),
        ],
        null=True,
    )
    description = models.TextField(null=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("pending", "pending"),
            ("resolved", "resolved"),
            ("active", "active"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " - " + self.city.name


class Announcement(models.Model):
    def get_24_hour_date(self):
        return self.date_posted + timedelta(hours=24)

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    message = models.TextField(null=True)
    display_image = models.ImageField(upload_to="announcements/", null=True, blank=True)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING)
    up_votes = models.IntegerField(default=0)
    expires = models.BooleanField(default=False)
    date_posted = models.DateTimeField(default=timezone.now)

    expires_at = models.DateTimeField(null=True, blank=True, editable=False)

    def save(self, *args, **kwargs):
        if self.expires:
            if not self.expires_at:
                self.expires_at = self.get_24_hour_date()
        else:
            self.expires_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class AnnouncementComment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    announcement = models.ForeignKey(
        Announcement,
        on_delete=models.CASCADE,
        related_name="announcement_comments",
        null=True,
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    up_votes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username + " - " + self.announcement.title


class PetLicensing(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    pet_name = models.CharField(max_length=50)
    species = models.CharField(max_length=50, null=True)
    breed = models.CharField(max_length=50, null=True)
    age = models.IntegerField()
    registration_date = models.DateField()
    expiration_date = models.DateField(null=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ("active", "active"),
            ("expired", "expired"),
            ("pending_renewal", "pending_renewal"),
        ],
    )
    fee = models.FloatField()
    vaccination_status = models.CharField(
        max_length=50, choices=[("pending", "pending"), ("vaccinated", "vaccinated")]
    )

    def __str__(self):
        return self.pet_name + " - " + self.property.address


class Tax(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    type = models.CharField(
        max_length=100,
        choices=[
            ("property", "property"),
            ("business", "business"),
            ("vehicle", "vehicle"),
            ("housing", "housing"),
        ],
    )
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    renewal_period = models.CharField(
        max_length=50,
        choices=[
            ("daily", "daily"),
            ("weekly", "weekly"),
            ("monthly", "monthly"),
            ("yearly", "yearly"),
            ("duty", "duty(once)"),
        ],
        null=True,
    )
    description = models.TextField(null=True)

    def __str__(self):
        return self.type + " - " + self.city.name


class TaxPayer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, related_name="tax_payers", null=True
    )
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tax_payer",
    )
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tax_payer",
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tax_payer",
    )
    total_tax_due = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    last_payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username


class TaxBill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tax_payer = models.ForeignKey(TaxPayer, on_delete=models.CASCADE)
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    status = models.CharField(
        max_length=50,
        choices=[("pending", "pending"), ("paid", "paid"), ("overdue", "overdue")],
        null=True,
        default="pending",
    )
    due_date = models.DateTimeField(null=True)

    def __str__(self):
        return self.tax_payer.user.username + " - " + self.tax.name


class TaxExemption(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    taxpayer = models.ForeignKey(
        TaxPayer, on_delete=models.CASCADE, related_name="exemptions"
    )
    tax = models.ForeignKey(Tax, on_delete=models.CASCADE)
    exemption_reason = models.TextField(null=True)
    discount_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True)

    def __str__(self):
        return self.taxpayer.user.username + " - " + self.tax.name


class Image(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    image = models.ImageField()
