from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class QueryType(str, Enum):
    """Enum for vehicle assistance query types"""

    INSTRUCTIONS = "question_for_instructions"
    DRIVING_LICENSE = "process_driving_licence_application"
    VEHICLE_TAX = "pay_vehicle_tax"
    OTHER = "other"


class VehicleAssistanceQueryType(BaseModel):
    query_type: QueryType = Field(description="The type of vehicle assistance query")


class DrivingLicenseApplication(BaseModel):
    """Structured data for a driving license application"""

    full_name: str = Field(description="Applicant's full name")
    date_of_birth: str = Field(description="Date of birth (DD/MM/YYYY)")
    address: str = Field(description="Full current address")
    phone_number: str = Field(description="Contact phone number")
    email: str = Field(description="Email address")
    previous_license_number: Optional[str] = Field(
        default=None, description="Previous license number if replacing"
    )


class CarTaxPayment(BaseModel):
    """Structured data for car tax payment"""

    vehicle_registration: str = Field(description="Vehicle registration number")
    make_model: str = Field(description="Vehicle make and model")
    owner_name: str = Field(description="Vehicle owner's name")


class InstructionResponse(BaseModel):
    """Response for instruction queries"""

    answer: str = Field(description="The detailed answer to the user's question")
