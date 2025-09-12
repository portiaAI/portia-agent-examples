import asyncio
import time

from models import CarTaxPayment, DrivingLicenseApplication


async def process_driving_license_application(
    application: DrivingLicenseApplication,
) -> str:
    """Process a driving license application"""
    # Simulate processing time
    await asyncio.sleep(2)

    return f"""✅ **Driving License Application Processed Successfully!**

Your application has been submitted with the following details:
- **Name**: {application.full_name}
- **Date of Birth**: {application.date_of_birth}  
- **Email**: {application.email}

**Next Steps:**
- You will receive a confirmation email within 24 hours
- Your new license will be processed within 10-15 working days
- You'll be notified when it's ready for collection or posted to your address

**Application Reference**: DVLA-{int(time.time())}"""


async def process_car_tax_payment(payment: CarTaxPayment) -> str:
    """Process a car tax payment"""
    # Simulate processing time
    await asyncio.sleep(2)

    return f"""✅ **Car Tax Payment Processed Successfully!**

Your vehicle tax has been paid for:
- **Vehicle**: {payment.vehicle_registration} ({payment.make_model})
- **Owner**: {payment.owner_name}
- **Amount Paid**: £165

**Important:**
- Your new tax disc information has been updated in the DVLA database
- You should receive confirmation within 2-3 working days
- No physical tax disc will be sent (digital system)
- Keep this confirmation for your records

**Payment Reference**: TAX-{int(time.time())}"""
