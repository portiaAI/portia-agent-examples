# ruff: noqa
import os
import asyncio
from decimal import Decimal
from typing import Optional
import secrets

from dotenv import load_dotenv
from portia import Portia, Config, Tool, ToolRunContext
from portia.cli import CLIExecutionHooks
from pydantic import BaseModel, Field
from typing import Type

load_dotenv(override=True)

def parse_token_balances(balance_response):
    """Parse token balances from CDP SDK response and return ETH and USDC balances."""
    balances = []
    if hasattr(balance_response, 'balances'):
        balances = balance_response.balances
    elif isinstance(balance_response, dict) and 'balances' in balance_response:
        balances = balance_response['balances']
    else:
        for item in balance_response:
            if isinstance(item, tuple) and len(item) == 2 and item[0] == 'balances':
                balances = item[1]
                break
    
    eth_balance = 0.0
    usdc_balance = 0.0
    
    for balance in balances:
        try:
            symbol = balance.token.symbol.upper()
            
            raw_amount = int(balance.amount.amount)
            decimals = int(balance.amount.decimals)
            actual_amount = raw_amount / (10 ** decimals)
            
            if symbol == 'ETH':
                eth_balance = actual_amount
            elif symbol == 'USDC':
                usdc_balance = actual_amount
                
            print(f"📊 {symbol}: {actual_amount} (raw: {raw_amount}, decimals: {decimals})")
                
        except Exception as e:
            print(f"Debug: Balance parsing error: {e}")
            print(f"Debug: Balance structure: {balance}")
            continue
    
    return eth_balance, usdc_balance

class USDCTransferInput(BaseModel):
    """Input schema for USDC transfer tool."""
    recipient_address: str = Field(
        description="The recipient's wallet address (0x...)"
    )
    amount: str = Field(
        description="Amount of USDC to send (e.g., '1' for 1 USDC)"
    )

class USDCTransferTool(Tool[str]):
    """Tool for transferring USDC to any wallet address (gasless)."""
    
    id: str = "usdc_transfer"
    name: str = "USDC Transfer Tool"
    description: str = "Send USDC to any wallet address using gasless transfers via CDP SDK"
    args_schema: Type[BaseModel] = USDCTransferInput
    output_schema: tuple[str, str] = (
        "text", 
        "A detailed message about the USDC transfer status including transaction hash"
    )
    
    def run(self, context: ToolRunContext, recipient_address: str, amount: str) -> str:
        """Execute USDC transfer."""
        try:
            if not recipient_address.startswith('0x') or len(recipient_address) != 42:
                return f"Error: Invalid recipient address format. Expected 0x followed by 40 characters, got: {recipient_address}"
            
            try:
                amount_decimal = Decimal(amount)
                if amount_decimal <= 0:
                    return "Error: Amount must be greater than 0"
            except Exception:
                return f"Error: Invalid amount format: {amount}"
            
            print(f"Initiating gasless USDC transfer of {amount} USDC to {recipient_address}...")
            
            result = asyncio.run(self._async_usdc_transfer(recipient_address, amount))
            return result
            
        except Exception as e:
            error_msg = f"Error executing USDC transfer: {str(e)}"
            print(error_msg)
            return error_msg
    
    async def _async_usdc_transfer(self, recipient_address: str, amount: str) -> str:
        """Async USDC transfer using CDP SDK."""
        from cdp import CdpClient, parse_units
        
        os.environ['CDP_API_KEY_ID'] = os.getenv('CDP_API_KEY_ID', '')
        os.environ['CDP_API_KEY_SECRET'] = os.getenv('CDP_API_KEY_SECRET', '')
        
        network_id = os.getenv('NETWORK_ID', 'base-sepolia')
        
        async with CdpClient() as cdp:
            try:
                wallet_private_key = os.getenv('WALLET_PRIVATE_KEY')
                
                if wallet_private_key and wallet_private_key != 'your_wallet_private_key_here':
                    if not wallet_private_key.startswith('0x'):
                        wallet_private_key = '0x' + wallet_private_key
                    
                    try:
                        account = await cdp.evm.import_account(
                            private_key=wallet_private_key,
                            name="imported-wallet"
                        )
                        print(f"✅ Imported wallet: {account.address}")
                    except Exception as e:
                        if "already_exists" in str(e):
                            account = await cdp.evm.get_or_create_account(name="imported-wallet")
                            print(f"✅ Using existing account: {account.address}")
                        else:
                            raise e
                else:
                    account = await cdp.evm.get_or_create_account(name="usdc-agent")
                    print(f"✅ Using account: {account.address}")
                
                # Check USDC balance
                try:
                    balance_response = await account.list_token_balances(
                        network="base-sepolia",
                    )
                    
                    eth_balance, usdc_balance = parse_token_balances(balance_response)
                    
                    requested_amount = float(amount)
                    
                    print(f"💰 Current USDC balance: {usdc_balance}")
                    print(f"🎯 Requested transfer amount: {requested_amount}")
                    
                    if usdc_balance < requested_amount:
                        return f"""
❌ Insufficient USDC balance!

💰 Current Balance: {usdc_balance} USDC  
🎯 Required Amount: {requested_amount} USDC
💸 Shortfall: {requested_amount - usdc_balance} USDC

🏦 Wallet Address: {account.address}
🚰 Fund your wallet with USDC and try again!

💡 You can get test USDC from faucets or transfer from another wallet.
"""
                except Exception as e:
                    print(f"⚠️ Could not check balance: {e}")
                
                print(f"🚀 Executing USDC transfer...")
                
                try:
                    tx = await account.transfer(
                        to=recipient_address,
                        amount=parse_units(amount, 6),
                        token="usdc",
                        network=network_id
                    )
                except Exception as error:
                    print(f"⚠️ Transfer failed: {error}")
                
                result = f"""
✅ USDC Transfer successful!
📊 Details:
   • Amount: {amount} USDC
   • To: {recipient_address}
   • From: {account.address}
   • Network: {network_id}
   • Type: Gasless
   • Transaction Hash: {tx}
   • Transaction Link: https://sepolia.basescan.org/tx/{tx}
"""
                
                print(result)
                return result
                
            except Exception as e:
                return f"❌ Transfer failed: {str(e)}"
    



class WalletInfoInput(BaseModel):
    """Input schema for wallet info tool (no parameters needed)."""
    pass

class WalletInfoTool(Tool[str]):
    """Tool for getting wallet information and balance."""
    
    id: str = "wallet_info"
    name: str = "Wallet Info Tool"
    description: str = "Get wallet address and balance information"
    args_schema: Type[BaseModel] = WalletInfoInput
    output_schema: tuple[str, str] = (
        "text",
        "Wallet information including address, network, and status"
    )
    
    def run(self, context: ToolRunContext) -> str:
        """Get wallet information."""
        try:
            result = asyncio.run(self._async_wallet_info())
            return result
            
        except Exception as e:
            error_msg = f"Error getting wallet info: {str(e)}"
            print(error_msg)
            return error_msg
    
    async def _async_wallet_info(self) -> str:
        """Async wallet info using CDP SDK."""
        from cdp import CdpClient
        
        # Configure authentication via environment variables
        os.environ['CDP_API_KEY_ID'] = os.getenv('CDP_API_KEY_ID', '')
        os.environ['CDP_API_KEY_SECRET'] = os.getenv('CDP_API_KEY_SECRET', '')
        
        async with CdpClient() as cdp:
            try:
                network_id = os.getenv('NETWORK_ID', 'base-sepolia')
                
                wallet_private_key = os.getenv('WALLET_PRIVATE_KEY')
                
                if wallet_private_key and wallet_private_key != 'your_wallet_private_key_here': 
                    if not wallet_private_key.startswith('0x'):
                        wallet_private_key = '0x' + wallet_private_key
                    
                    try:
                        account = await cdp.evm.import_account(
                            private_key=wallet_private_key,
                            name="imported-wallet"
                        )
                        wallet_type = "Imported Wallet"
                        print(f"✅ Imported wallet: {account.address}")
                    except Exception as e:
                        if "already_exists" in str(e):
                            account = await cdp.evm.get_or_create_account(name="imported-wallet")
                            wallet_type = "Existing Account"
                            print(f"✅ Using existing account: {account.address}")
                        else:
                            raise e
                else:
                    account = await cdp.evm.get_or_create_account(name="usdc-agent")
                    wallet_type = "Managed Account"
                    print(f"✅ Using account: {account.address}")
                
                try:
                    balance_response = await account.list_token_balances(
                        network=network_id,
                    )
                    
                    eth_balance, usdc_balance = parse_token_balances(balance_response)
                    
                    balance_info = f"""
   • ETH Balance: {eth_balance} ETH
   • USDC Balance: {usdc_balance} USDC"""
                except Exception as e:
                    balance_info = f"""
   • Balance: Unable to fetch ({str(e)[:50]}...)"""
                
                result = f"""
💰 Wallet Information:
   • Address: {account.address}
   • Network: {network_id}  
   • Type: {wallet_type}
{balance_info}
   
🎯 Ready for USDC transfers!
✨ Gasless USDC transfers supported (no ETH needed for gas)
💡 Fund with USDC to start sending payments

Available commands:
• 'send [amount] USDC to [address]' - Send USDC 
• 'send 5 USDC to 0x123...' - Example transfer
"""
                
                print(result)
                return result
                
            except Exception as e:
                return f"❌ Error getting wallet info: {str(e)}"
    



def main():
    """Main function to run the crypto agent."""
    
    required_env_vars = [
        'CDP_API_KEY_ID',
        'CDP_API_KEY_SECRET', 
        'PORTIA_API_KEY'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   • {var}")
        print("\nPlease create a .env file with the required variables.")
        return
    
    wallet_key = os.getenv('WALLET_PRIVATE_KEY')
    if wallet_key and wallet_key.strip():
        print("🔑 Using imported wallet from WALLET_PRIVATE_KEY")
    else:
        print("🆕 Will create new wallets automatically")
    
    network_id = os.getenv('NETWORK_ID', 'base-sepolia')
    print(f"🚀 Starting USDC Transfer Agent on {network_id} network...")
    
    usdc_tool = USDCTransferTool()
    wallet_tool = WalletInfoTool()
    
    config = Config.from_default()
    tools = [usdc_tool, wallet_tool]
    
    portia = Portia(
        config=config,
        tools=tools,
        execution_hooks=CLIExecutionHooks()
    )
    
    print("💡 Available commands:")
    print("   • 'wallet info' - Create wallet and get ready for transfers")  
    print("   • 'send [amount] USDC to [address]' - Send USDC (gasless)")
    print("   • 'send 5 USDC to 0x742d35Cc...' - Example USDC transfer")
    print("\n✨ All USDC transfers are gasless - no ETH needed!")
    print("=" * 60)
    
    while True:
        try:
            user_query = input("\n🔮 Enter your command (or 'quit' to exit): ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_query:
                continue
                
            plan_run = portia.run(user_query)
            
            if plan_run.outputs.final_output:
                print(f"\n{plan_run.outputs.final_output.value}")
            else:
                print("No output generated.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
