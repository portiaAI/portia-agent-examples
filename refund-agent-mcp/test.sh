#!/bin/bash

set -e
logfile="log_$(date +%Y%m%d_%H%M%S).txt"
echo "Setting up Stripe user and payment"
uv run python stripe_setup.py --email test@portialabs.ai >> $logfile 2>&1
echo "Running success case - AI should refund..."
yes | uv run python refund_agent.py --email test@portialabs.ai >> $logfile 2>&1
echo "Running error case - AI should not refund, should exit normally with no refund..."
uv run python refund_agent.py --email test@portialabs.ai --request "I sat on my hoverboard and it broke. I want a refund." >> $logfile 2>&1
echo "Running error case - Human rejects refund, should fail with error..."
yes N | uv run python refund_agent.py --email test@portialabs.ai >> $logfile 2>&1
echo "Done"