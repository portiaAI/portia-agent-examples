from typing import Optional

from pydantic import BaseModel, Field


class DVLAQueryType(BaseModel):
    query_type: str = Field(
        description="The type of DVLA query",
        enum=[
            "question_for_instructions",
            "process_driving_licence_application",
            "pay_vehicle_tax",
            "other",
        ],
    )


class DrivingLicenseApplication(BaseModel):
    """Structured data for a driving license application"""

    full_name: str = Field(description="Applicant's full name")
    date_of_birth: str = Field(description="Date of birth (DD/MM/YYYY)")
    address: str = Field(description="Full current address")
    phone_number: str = Field(description="Contact phone number")
    email: str = Field(description="Email address")
    license_type: str = Field(
        description="Type of license (e.g., full car, motorcycle, provisional)"
    )
    previous_license_number: Optional[str] = Field(
        default=None, description="Previous license number if replacing"
    )


class CarTaxPayment(BaseModel):
    """Structured data for car tax payment"""

    vehicle_registration: str = Field(description="Vehicle registration number")
    make_model: str = Field(description="Vehicle make and model")
    vehicle_type: str = Field(
        description="Type of vehicle (car, van, motorcycle, etc.)"
    )
    engine_size: Optional[str] = Field(
        default=None, description="Engine size or power rating"
    )
    fuel_type: str = Field(description="Fuel type (petrol, diesel, electric, hybrid)")
    tax_period: str = Field(description="Tax period (6 months, 12 months)")
    owner_name: str = Field(description="Vehicle owner's name")


class InstructionResponse(BaseModel):
    """Response for instruction queries"""

    answer: str = Field(description="The detailed answer to the user's question")
