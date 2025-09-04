"""Example evals runs."""

from typing import Any
from portia import (
    Config,
    LogLevel,
)
from steelthread.portia.tools import ToolStubContext, ToolStubRegistry

# from evals.data import REFUND_POLICY, CUSTOM_REQUEST
from refund_agent import get_portia

from steelthread.evals import EvalConfig
from steelthread.steelthread import (
    SteelThread,
)

REFUND_POLICY = """**Refund Policy for Hoverfly PLC**

At Hoverfly PLC, we are proud to offer the world’s first gravity-defying hoverboards. We are committed to ensuring your satisfaction, and we have established this Refund Policy to clarify the conditions under which refunds are granted. Please read this policy carefully before initiating a refund request.

---

### 1. Eligibility for Refunds

- **Time Frame:** Refund requests must be submitted within **30 days** from the date of purchase.
- **Condition of Product:** Refunds are processed only if the hoverboard is returned in an **as-new condition**. This means:
  - The product is unused and undamaged.
  - It is returned in its original packaging with all accessories, manuals, and warranty information intact.
  - There are no signs of wear, modification, or improper use.
- **Defective Products:** If the product proves to be defective within the Refund Time Frame, assuming the the Condition of the Product is as described, it can be refunded.
- **Exceptions:** Custom orders, personalized items, or products marked as non-refundable at the time of purchase are not eligible for refunds, unless the item is defective upon arrival.

---

### 2. Initiating a Refund Request

- **Contact Us:** To begin the refund process, please contact our Customer Service team at [insert contact email/phone]. Include your order number, a description of the issue, and (if applicable) photographs showing the product’s condition.
- **Return Authorization:** Once your request is received, our team will verify the eligibility of your refund. If approved, you will receive a Return Authorization Number (RAN) along with detailed return instructions.

---

### 3. Return Shipping

- **Customer Responsibility:** Unless the product is defective or not as described, the customer is responsible for the return shipping costs.
- **Packaging:** Please ensure the hoverboard is securely packaged to prevent damage during transit. We recommend using a trackable shipping service or purchasing shipping insurance.

---

### 4. Inspection and Approval

- **Product Inspection:** Upon receipt of your returned hoverboard, our team will inspect the product to confirm it meets the “as-new” criteria.
- **Approval:** If the product passes inspection, we will proceed with processing your refund.
- **Denial:** If the hoverboard does not meet the required condition, we reserve the right to deny the refund request and return the product to you.

---

### 5. Refund Processing

- **Method of Refund:** Approved refunds will be issued using the original method of payment.
- **Processing Time:** Please allow 7–10 business days for the refund to be credited to your account after approval.
- **Deductions:** Any initial shipping or handling fees may be deducted from your refund unless the return is due to a defect or an error on our part.

---

### 6. Exchanges and Store Credit

- **Exchanges:** If you prefer to exchange your hoverboard for a different model or product, please contact our Customer Service team to discuss available options.
- **Store Credit:** In some cases, we may offer store credit instead of a cash refund. This will be communicated to you on a case-by-case basis.

---

### 7. Policy Updates

- **Modifications:** Hoverfly PLC reserves the right to modify or update this Refund Policy at any time. Any changes will be posted on our website with the new effective date.
- **Review:** We encourage you to review this policy periodically to stay informed of any updates.

---

### 8. Contact Information

If you have any questions or need further assistance regarding our refund policy, please contact our Customer Service team at [insert contact email/phone].

Thank you for choosing Hoverfly PLC. We are dedicated to providing innovative products and exceptional service, and we appreciate your business."""


CUSTOM_REQUEST = """---header---
From: Marty McFly <email: tom@portialabs.ai>
To: support@hoverfly.com
Subject: Refund request
---header---
---body---
Hi,
I've changed my mind about my custom hoverboard, its still working but I dont like the colour. Can I get a refund

Thanks,
Marty McFly
---body---"""

APPROVED_REQUEST = """---header---
From: Marty McFly <email: tom@portialabs.ai>
To: support@hoverfly.com
Subject: Refund request
---header---
---body---
Hi,
I bought one of your hoverboards 3 days ago. When I took it out of the box and turned it on, 
it did not work. Please can I get a refund?

Thanks,
Marty McFly
---body---"""


REJECTED_TIME_REQUEST = """---header---
From: Marty McFly <email: tom@portialabs.ai>
To: support@hoverfly.com
Subject: Refund request
---header---
---body---
Hi,
I bought one of your hoverboards 2 years ago. When I took it out of the box and turned it on, 
it did not work. Please can I get a refund?

Thanks,
Marty McFly
---body---"""


REJECTED_DAMAGE_REQUEST = """---header---
From: Marty McFly <email: tom@portialabs.ai>
To: support@hoverfly.com
Subject: Refund request
---header---
---body---
Hi,

I dropped my Hoverboard in the flux-capacitor, can I get a refund?

Thanks,
Marty McFly
---body---"""


REJECTED_PACKAGING_REQUEST = """---header---
From: Marty McFly <email: tom@portialabs.ai>
To: support@hoverfly.com
Subject: Refund request
---header---
---body---
Hi,

I would like a refund on my hoverboard but I've lost the original packaging...

Thanks,
Marty McFly
---body---"""

# Setup config + Steel Thread
config = Config.from_default(
    default_log_level=LogLevel.CRITICAL,
)
st = SteelThread()


def file_reader_stub(
    ctx: ToolStubContext,
) -> str:
    """Stub for file reader."""
    file_name = ctx.kwargs.get("filename", "").lower()
    if file_name == "inbox.txt":
        match ctx.test_case_name:
            case "approved":
                return APPROVED_REQUEST
            case "rejected_damage":
                return REJECTED_DAMAGE_REQUEST
            case "rejected_time":
                return REJECTED_TIME_REQUEST
            case "rejected_package":
                return REJECTED_PACKAGING_REQUEST
            case "rejected_custom":
                return CUSTOM_REQUEST
    if file_name == "refund_policy.txt":
        return REFUND_POLICY

    return f"Unknown file: {file_name}"


def email_stub(
    ctx: ToolStubContext,
) -> str:
    """stub for email tool"""
    return "Sent email with id: 1990ad986f4b273d"


def stripe_list_customers_stub(
    ctx: ToolStubContext,
) -> dict[str, Any]:
    """stub for stripe list customers tool"""
    return {
        "meta": None,
        "content": [
            {
                "type": "text",
                "text": '[{"id":"cus_SynR16vHDHQaaP"}]',
                "annotations": None,
                "meta": None,
            }
        ],
        "structuredContent": None,
        "isError": None,
    }


def stripe_list_intents_stub(
    ctx: ToolStubContext,
) -> dict[str, Any]:
    """stub for stripe refund tool"""
    return {
        "meta": None,
        "content": [
            {
                "type": "text",
                "text": [
                    {
                        "id": "pi_3222pr2JzejAAAE2103JSnfWt",
                        "object": "payment_intent",
                        "amount": 1000,
                        "amount_capturable": 0,
                        "amount_details": {"tip": {}},
                        "amount_received": 1000,
                        "application": None,
                        "application_fee_amount": None,
                        "automatic_payment_methods": None,
                        "canceled_at": None,
                        "cancellation_reason": None,
                        "capture_method": "automatic",
                        "confirmation_method": "automatic",
                        "created": 1756802776,
                        "currency": "gbp",
                        "customer": "cus_SynR16vXWFQaaP",
                        "description": "Payment for Invoice",
                        "excluded_payment_method_types": None,
                        "last_payment_error": None,
                        "latest_charge": "ch_3S2pr2JzejWEsE210XxB6Ag0",
                        "livemode": False,
                        "metadata": {},
                        "next_action": None,
                        "on_behalf_of": None,
                        "payment_method": "pm_1S2pqzJzejWEjEssss21M6z3LJ43",
                        "payment_method_configuration_details": None,
                        "payment_method_options": {
                            "card": {
                                "installments": None,
                                "mandate_options": None,
                                "network": None,
                                "request_three_d_secure": "automatic",
                            },
                            "klarna": {"preferred_locale": None},
                            "link": {"persistent_token": None},
                            "revolut_pay": {},
                        },
                        "payment_method_types": [
                            "card",
                            "klarna",
                            "link",
                            "revolut_pay",
                        ],
                        "processing": None,
                        "receipt_email": None,
                        "review": None,
                        "setup_future_usage": None,
                        "shipping": None,
                        "source": None,
                        "statement_descriptor": None,
                        "statement_descriptor_suffix": None,
                        "status": "succeeded",
                        "transfer_data": None,
                        "transfer_group": None,
                    }
                ],
                "annotations": None,
                "meta": None,
            }
        ],
        "structuredContent": None,
        "isError": False,
    }


def stripe_refund_stub(
    ctx: ToolStubContext,
) -> dict[str, Any]:
    """stub for stripe refund tool"""
    return {
        "meta": None,
        "content": [
            {
                "type": "text",
                "text": {
                    "id": "re_3S2pr2JzejWEjE210m3qqgRu",
                    "status": "succeeded",
                    "amount": 1000,
                },
                "annotations": None,
                "meta": None,
            }
        ],
        "structuredContent": None,
        "isError": False,
    }


# Run evals
portia = get_portia()
portia.tool_registry = ToolStubRegistry(
    registry=portia.tool_registry,
    stubs={
        "file_reader_tool": file_reader_stub,
        "portia:mcp:mcp.stripe.com:list_customers": stripe_list_customers_stub,
        "portia:mcp:mcp.stripe.com:list_payment_intents": stripe_list_intents_stub,
        "portia:mcp:mcp.stripe.com:create_refund": stripe_refund_stub,
        "portia:google:gmail:send_email": email_stub,
    },
)
st.run_evals(
    portia,
    EvalConfig(
        eval_dataset_name="portia-default::refund-agent",
        config=config,
        iterations=4,
    ),
)
