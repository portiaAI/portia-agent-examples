poetry sync
echo "Setting up Stripe user and payment"
poetry run python stripe_setup.py --email test@portialabs.ai 
echo "Running success case - AI should refund"
yes | poetry run python refund_agent.py --email test@portialabs.ai # | tail -n 1
echo "Running error case - AI should not refund..."
poetry run python refund_agent.py --email test@portialabs.ai --request "I sat on my hoverboard and it broke. I want a refund." # | tail -n 1
echo "Running error case - Human rejects refund..."
yes N | poetry run python refund_agent.py --email test@portialabs.ai # | tail -n 1
echo "Done"