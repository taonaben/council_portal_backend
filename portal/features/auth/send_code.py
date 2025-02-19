from django.core.mail import send_mail
import random
import string

from portal.models import VerificationCode


def generate_code():
    return "".join(random.choices(string.digits, k=6))


def send_verification_code_via_email(user):
    code = generate_code()
    VerificationCode.objects.create(user=user, code=code)

    send_mail(
        "Your Verification Code",
        f"Your verification code is {code}. It expires in 5 minutes.",
        "no-reply@example.com",
        [user.email],
        fail_silently=False,
    )


def send_verification_code_via_sms(user):
    code = generate_code()
    VerificationCode.objects.create(user=user, code=code)

    # Assuming you have a function `send_sms` to send SMS
    send_sms(
        user.phone_number, f"Your verification code is {code}. It expires in 5 minutes."
    )


def send_sms(phone_number, message):
    # Implement your SMS sending logic here
    print(f"Sending SMS to {phone_number}: {message}")
