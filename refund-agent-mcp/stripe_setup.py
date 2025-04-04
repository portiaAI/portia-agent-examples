"""
Script to set up a Stripe test environment for the refund agent example.

This script creates a state where we have a customer that has paid for a product.

Args:
    --email: The email address of the customer to create.
"""
import json
import os
import stripe
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

# Initialize Stripe with the API key
stripe.api_key = os.getenv("STRIPE_TEST_API_KEY")


def setup_stripe_test_environment(customer_email):
    """
    Sets up a Stripe test environment with:
    1. A customer
    2. A product
    3. A payment (via invoice)
    """
    try:
        # 1. Create a customer
        payment_method = stripe.PaymentMethod.retrieve("pm_card_visa")
        customer = stripe.Customer.create(
            email=customer_email,
            description="Test customer for refund example",
            payment_method=payment_method.id,
        )
        print(f"Created customer: {customer.id}")

        # 2. Create a product
        product = stripe.Product.create(
            name="Hoverboard", description="A futuristic personal transportation device"
        )
        print(f"Created product: {product.id}")

        # Create a price for the product
        price = stripe.Price.create(
            product=product.id,
            unit_amount=1000,  # $10.00
            currency="gbp",
        )
        print(f"Created price: {price.id}")

        # Create the invoice
        invoice = stripe.Invoice.create(
            customer=customer.id,
            auto_advance=True,  # Automatically finalize the invoice
        )
        invoice.add_lines(lines=[{"pricing": {"price": price.id}, "quantity": 1}])
        print(f"Created invoice: {invoice.id}")
        # Finalize and pay the invoiceid)
        paid_invoice = stripe.Invoice.pay(
            invoice=invoice.id, payment_method=payment_method.id
        )
        print(f"Paid invoice: {paid_invoice.id}")
        return {
            "customer_id": customer.id,
            "product_id": product.id,
            "price_id": price.id,
            "invoice_id": paid_invoice.id,
        }

    except stripe.error.StripeError as e:
        print(f"Stripe error occurred: {e}")
        raise


if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Set up a Stripe test environment")
    parser.add_argument("--email", required=True, help="Customer email address")

    # Parse arguments
    args = parser.parse_args()

    # Run the setup with the provided email
    result = setup_stripe_test_environment(args.email)
    print("Final result:")
    print(json.dumps(result, indent=4))
