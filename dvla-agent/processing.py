import asyncio
import time

import streamlit as st
from models import CarTaxPayment, DrivingLicenseApplication


async def process_driving_license_application(
    application: DrivingLicenseApplication,
) -> str:
    """Process a driving license application"""
    # Simulate processing time
    await asyncio.sleep(2)

    # Create the formatted message
    license_message = f"""✅ **Driving License Application Processed Successfully!**

Your application has been submitted with the following details:
- **Name**: {application.full_name}
- **Date of Birth**: {application.date_of_birth}  
- **License Type**: {application.license_type}
- **Email**: {application.email}

**Next Steps:**
- You will receive a confirmation email within 24 hours
- Your new license will be processed within 10-15 working days
- You'll be notified when it's ready for collection or posted to your address

**Application Reference**: DVLA-{int(time.time())}"""

    # Add message directly to chat
    st.session_state.messages.append({"role": "assistant", "content": license_message})

    # Return simple success indicator
    return "DRIVING_LICENSE_PROCESSED"


async def process_car_tax_payment(payment: CarTaxPayment) -> str:
    """Process a car tax payment"""
    # Simulate processing time
    await asyncio.sleep(2)

    # Calculate mock tax amount based on vehicle type and period
    base_rates = {
        "car": {"6 months": 85, "12 months": 165},
        "van": {"6 months": 140, "12 months": 270},
        "motorcycle": {"6 months": 25, "12 months": 47},
    }

    vehicle_category = "car"  # Default
    if "van" in payment.vehicle_type.lower():
        vehicle_category = "van"
    elif (
        "motorcycle" in payment.vehicle_type.lower()
        or "bike" in payment.vehicle_type.lower()
    ):
        vehicle_category = "motorcycle"

    tax_amount = base_rates[vehicle_category].get(payment.tax_period, 165)

    # Create the formatted message
    tax_message = f"""✅ **Car Tax Payment Processed Successfully!**

Your vehicle tax has been paid for:
- **Vehicle**: {payment.vehicle_registration} ({payment.make_model})
- **Owner**: {payment.owner_name}
- **Tax Period**: {payment.tax_period}
- **Amount Paid**: £{tax_amount}

**Important:**
- Your new tax disc information has been updated in the DVLA database
- You should receive confirmation within 2-3 working days
- No physical tax disc will be sent (digital system)
- Keep this confirmation for your records

**Payment Reference**: TAX-{int(time.time())}"""

    # Add message directly to chat
    st.session_state.messages.append({"role": "assistant", "content": tax_message})

    # Return simple success indicator
    return "CAR_TAX_PROCESSED"
