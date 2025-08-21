# Portia USDC Agent

## Introduction
The Portia USDC Agent is an automated cryptocurrency transfer assistant that allows you to send gasless USDC to any EVVM wallet address using the Coinbase Developer Platform (CDP) SDK. This agent provides a simple, secure way to:

- Send gasless USDC to any EVM wallet address
- Check wallet balance and information  
- Execute transactions on multiple blockchain networks
- Use natural language commands to perform crypto operations

Currently supported:
- **Networks**: Base Sepolia (testnet), Base Mainnet, Ethereum Sepolia, Ethereum Mainnet
- **Wallet Types**: Any EVM wallet that can be imported via private key

## Prerequisites
- Python 3.11+
- A Coinbase Developer Platform account and API keys
- A crypto wallet with a private key (recommended to create a new wallet)
- The Portia SDK installed  
- uv (Python package installer) - Install it using:
  ```bash
  pip install uv
  ```

## Setup

### 1. Clone and Navigate
```bash
git clone https://github.com/portiaAI/portia-agent-examples.git
cd portia-agent-examples/usdc-agent
```

### 2. Environment Configuration
Copy the example environment file and configure your credentials:
```bash
cp env.example .env
```

Edit `.env` and add your credentials:

#### Required Variables:
- **`CDP_API_KEY_ID`**: Your CDP API key ID from [Coinbase Developer Platform](https://portal.cdp.coinbase.com/access/api)
- **`CDP_API_KEY_SECRET`**: Your CDP API key secret (keep this secure!)
- **`CDP_WALLET_SECRET`**: Your CDP Wallet secret (keep this secure!)
- **`WALLET_PRIVATE_KEY`**: Your wallet's private key (64 character hex string, with or without 0x prefix)
- **`PORTIA_API_KEY`**: Your Portia API key from [Portia Settings](https://app.portia.ai/settings)

#### Optional Variables:
- **`NETWORK_ID`**: Blockchain network (default: `base-sepolia`)
  - Supported: `base-sepolia`, `base`, `ethereum-sepolia`, `ethereum`
- **LLM API Key**: Choose one - `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `TOGETHER_API_KEY`

### 3. Coinbase Developer Platform Setup

1. Visit [Coinbase Developer Platform](https://portal.cdp.coinbase.com/)
2. Create an account and verify your identity
3. Navigate to "Dashboard" → "Creat API Key" 
4. Create a new API key and save both the api key id and private key
5. Create a wallet secret and save it
5. Add these to your `.env` file

### 4. Wallet Setup

**For Testing (Recommended):**
- Use a testnet wallet with small amounts
- Get testnet USDC on Base Sepolia from [Circle Faucet](https://faucet.circle.com/)

**For Production:**
- Use a dedicated wallet for the agent
- Never use your main wallet's private key
- Consider using a multi-sig wallet for larger amounts

### 5. Test Setup
Test if the setup is properly configured or not
```bash
uv run test_setup.py
```
## Usage

### Start the Agent
```bash
uv run main.py
```

### Available Commands

The agent accepts natural language commands:

#### Check Wallet Information:
```
wallet info
show my balance
what's my wallet address
```

#### Send Cryptocurrency:
```
send 0.01 to 0x742d35Cc6Bf42BaaCbf58E4b99C1E6b0E1Bf8F8f
transfer 10 USDC to 0x123...abc  
send 0.5 USDC to my friend's wallet 0x456...def
```

#### Examples:
```
🔮 Enter your command: wallet info
💰 Wallet Information:
   • Address: 0x1234567890123456789012345678901234567890
   • Network: base-sepolia  
   • ETH Balance: 0.05

🔮 Enter your command: send 0.01 ETH to 0x742d35Cc6Bf42BaaCbf58E4b99C1E6b0E1Bf8F8f
✅ Transfer successful!
📊 Details:
   • Amount: 0.01 ETH
   • To: 0x742d35Cc6Bf42BaaCbf58E4b99C1E6b0E1Bf8F8f
   • Network: base-sepolia
   • Transaction Hash: 0xabc123...
   • Transaction Link: https://sepolia.basescan.org/tx/0xabc123...
```

## Understanding the Code

### `main.py`
The main entry point that:
- Sets up environment configuration
- Initializes CDP SDK and Portia framework
- Provides interactive command interface
- Handles user input and executes transactions

### Key Components:

#### `CryptoTransferTool`
- Handles cryptocurrency transfers
- Validates wallet addresses and amounts
- Executes transactions via CDP SDK
- Returns transaction details and links

#### `WalletInfoTool`  
- Retrieves wallet address and balance
- Displays network information
- Provides account overview

## Security Best Practices

⚠️ **Important Security Notes:**

1. **Never commit your `.env` file** - It contains sensitive private keys
2. **Use testnet first** - Always test on Base Sepolia before mainnet
3. **Dedicated wallet** - Use a separate wallet for the agent, not your main one
4. **Small amounts** - Start with small test amounts
5. **Verify addresses** - Always double-check recipient addresses
6. **Secure storage** - Store private keys securely and never share them

## Supported Networks

| Network | Network ID | Description |
|---------|------------|-------------|
| Base Sepolia | `base-sepolia` | Base testnet (recommended for testing) |
| Base Mainnet | `base` | Base production network |
| Ethereum Sepolia | `ethereum-sepolia` | Ethereum testnet |  
| Ethereum Mainnet | `ethereum` | Ethereum production network |

## Supported Assets

- **USDC** - USDC Coin stablecoin

## Troubleshooting

### Common Issues:

**"CDP API credentials not found"**
- Ensure `CDP_API_KEY_NAME` and `CDP_API_KEY_PRIVATE_KEY` are set in `.env`

**"WALLET_PRIVATE_KEY not found"**
- Add your wallet's private key to the `.env` file (without 0x prefix)

**"Invalid recipient address format"**
- Ensure address starts with 0x and is 42 characters total
- Example: `0x742d35Cc6Bf42BaaCbf58E4b99C1E6b0E1Bf8F8f`

**"Insufficient funds"**
- Check your wallet balance with `wallet info`
- Ensure you have enough ETH for both the transfer and gas fees

**Transaction fails**
- Verify the network is correct (testnet vs mainnet)
- Check if the recipient address is valid for the network
- Ensure sufficient gas fees

### Getting Help:
1. Check the [CDP SDK Documentation](https://docs.cdp.coinbase.com/)
2. Visit [Portia Documentation](https://docs.portia.ai/)
3. Test on testnet first before reporting issues

## License
This project follows the same license as the parent repository.
