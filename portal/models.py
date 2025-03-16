from datetime import timedelta, datetime, date

import random
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
import string
from django.utils import timezone

review_enums = {
    "pending": "pending",
    "approved": "approved",
    "denied": "denied",
}


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
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


class User(AbstractUser):
    is_active = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, unique=True, null=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)


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
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
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
    tax = models.ForeignKey("Tax", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address + " - " + self.owner.username + "(" + self.city.name + ")"


class WaterBill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    water_used = models.FloatField()
    meter_number = models.IntegerField()
    amount_owed = models.FloatField()
    amount_paid = models.FloatField(null=True)
    status = models.CharField(
        max_length=50,
        choices=[("pending", "pending"), ("paid", "paid")],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.property.address + " - " + str(self.amount)


class WaterMeter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meter_num = models.CharField(unique=True, max_length=20)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    current_reading = models.FloatField(default=0.0)

    def __str__(self):
        return str(self.meter_num) + " - " + self.property.address

    def generate_meter_num(self):
        values = string.digits
        num = "".join(random.choice(values) for _ in range(10))

        first_val = self.property.community.name[0]
        return first_val.upper() + num + "25"

    def save(self, *args, **kwargs):
        if not self.meter_num:
            self.meter_num = self.generate_meter_num()
        super().save(*args, **kwargs)

    def update_reading(self, new_reading):
        if new_reading != self.current_reading:
            WaterUsage.objects.create(
                meter=self,
                property=self.property,
                consumption=new_reading - self.current_reading,
                date_recorded=timezone.now(),
            )
            self.current_reading = new_reading
            self.save()


class WaterUsage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    meter = models.ForeignKey(WaterMeter, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    consumption = models.FloatField()
    date_recorded = models.DateTimeField()


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
    registered_at = models.DateTimeField(auto_now_add=True)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    car = models.ForeignKey(
        Vehicle, on_delete=models.CASCADE, related_name="parking_tickets"
    )
    city = models.ForeignKey(
        City, on_delete=models.DO_NOTHING, related_name="parking_tickets", null=True
    )
    issued_at = models.DateTimeField(auto_now_add=True)
    time_in = models.TimeField(null=True, blank=True)
    expiry_at = models.DateTimeField(null=True, blank=True)
    amount = models.FloatField(null=False, default=0)

    ISSUED_LENGTH_CHOICES = [
        ("30min", "30 Minutes"),
        ("1hr", "1 Hour"),
        ("2hr", "2 Hours"),
        ("3hr", "3 Hours"),
    ]

    issued_length = models.CharField(
        max_length=10, choices=ISSUED_LENGTH_CHOICES, default="30min"
    )

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("used", "Used"),
        ("expired", "Expired")
    ]

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="inactive")

    def get_issues_time(self):
        return {
            "30min": 30,
            "1hr": 60,
            "2hr": 120,
            "3hr": 180,
        }.get(self.issued_length, 30)

    def get_amount(self):
        return {
            "30min": 1,
            "1hr": 2,
            "2hr": 4,
            "3hr": 6,
        }.get(self.issued_length, 1)

    def update_status(self):
        """Automatically updates the status based on expiry time."""
        now = timezone.now()
        if self.expiry_at and now >= self.expiry_at:
            self.status = "expired"

    def activate_ticket(self):
        """Activates the ticket by setting the status to 'active' and calculates expiry."""
        if self.status == "inactive":
            self.status = "active"
            self.time_in = timezone.now()
            self.expiry_at = self.time_in + timedelta(minutes=self.get_issues_time())
            self.save()

    def save(self, *args, **kwargs):
        """Ensures correct values are set before saving."""
        if not self.expiry_at:  # Ensure expiry is only set once
            if self.issued_at:
                self.expiry_at = self.time_in + timedelta(
                    minutes=self.get_issues_time()
                )

        if self.amount == 0:  # Avoid overwriting manually set amounts
            self.amount = self.get_amount()

        self.update_status()  # Update status before saving

        super().save(*args, **kwargs)

    def extend_ticket(self, additional_time):
        """
        Allows the user to extend their parking ticket.
        `additional_time` should be one of ['30min', '1hr', '2hr', '3hr'].
        """
        if self.status == "expired":
            raise ValueError("Cannot extend an expired ticket.")

        extra_minutes = {
            "30min": 30,
            "1hr": 60,
            "2hr": 120,
            "3hr": 180,
        }.get(additional_time, 0)

        extra_amount = {
            "30min": 1,
            "1hr": 2,
            "2hr": 4,
            "3hr": 6,
        }.get(additional_time, 0)

        if extra_minutes > 0:
            if self.expiry_at:
                self.expiry_at += timedelta(minutes=extra_minutes)  # Extend expiry time
            else:
                self.expiry_at = self.issued_at + timedelta(minutes=extra_minutes)
            self.amount += extra_amount  # Add cost
            self.save()

    def __str__(self):
        return (
            f"{self.car.plate_number} - {self.issued_at.strftime('%Y-%m-%d %H:%M:%S')}"
        )

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
