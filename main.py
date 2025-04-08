import requests
import json
from tinydb import TinyDB

wallets = [
    "0xYourWalletAddress1",
    "0xYourWalletAddress2"
]

RPC_ENDPOINT = "https://rpc.hyperliquid.xyz/evm"
HYPERCORE_API_ENDPOINT = "https://api.hyperliquid.xyz/info"

# Initialize TinyDB
db = TinyDB('balances.json')

def get_balance(wallet):
    # Build the JSON-RPC payload for method eth_getBalance
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "eth_getBalance",
        "params": [wallet, "latest"]
    }
    response = requests.post(RPC_ENDPOINT, json=payload)
    data = response.json()
    # Convert hex balance to integer
    wei_balance = int(data["result"], 16)
    return wei_balance / (10 ** 18)

def get_hype_price():
    """Fetch the current HYPE price in USD using Pyth Oracle via Hermes API v2"""
    try:
        # HYPE price feed ID for Pyth
        hype_feed_id = "0x4279e31cc369bbcc2faf022b382b080e32a8e689ff20fbc530d2a603eb6cd98b"
        
        # Using Hermes API v2 to get the latest price from Pyth
        url = f"https://hermes.pyth.network/v2/updates/price/latest?ids%5B%5D={hype_feed_id}"
        
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Error fetching price: {response.status_code}")
            return None
        
        data = response.json()
        if not data or "parsed" not in data or len(data["parsed"]) == 0:
            print("No price data received")
            return None
        
        # Extract the price from the response
        price_feed = data["parsed"][0]
        price_info = price_feed.get("price", {})
        
        # Calculate actual price using price and expo values
        price = float(price_info.get("price", 0)) * (10 ** price_info.get("expo", 0))
        return price
    except Exception as e:
        print(f"Error getting HYPE price: {str(e)}")
        return None

def get_hypercore_balance(wallet):
    """Fetch token balances from HyperCore (Hyperliquid L1)"""
    try:
        payload = {
            "type": "spotClearinghouseState",
            "user": wallet
        }
        response = requests.post(HYPERCORE_API_ENDPOINT, json=payload)
        if response.status_code != 200:
            print(f"Error fetching HyperCore balance for {wallet}: {response.status_code}")
            return []
        
        data = response.json()
        if not data or "balances" not in data:
            print(f"No balance data received for {wallet}")
            return []
        
        return data["balances"]
    except Exception as e:
        print(f"Error getting HyperCore balance for {wallet}: {str(e)}")
        return []

def get_staking_balance(wallet):
    """Fetch delegated staking balances from HyperCore (Hyperliquid L1)"""
    try:
        payload = {
            "type": "delegatorSummary",
            "user": wallet
        }
        response = requests.post(HYPERCORE_API_ENDPOINT, json=payload)
        if response.status_code != 200:
            print(f"Error fetching staking balance for {wallet}: {response.status_code}")
            return None
        
        data = response.json()
        if not data:
            return None
        
        return data
    except Exception as e:
        print(f"Error getting staking balance for {wallet}: {str(e)}")
        return None

def main():
    # Display previous balances from TinyDB if available
    previous = db.all()
    if previous:
        print("Previous HYPE Token Balances:")
        for record in previous:
            if "type" not in record or record["type"] == "evm":
                print(f"Wallet: {record['wallet']} - Balance: {record['balance']:.4f} HYPE")
        print("-------------------------")
    
    # Get EVM balances
    total_evm_balance = 0
    print("Current HYPE Token Balances (EVM):")
    current_run = []
    for wallet in wallets:
        balance = get_balance(wallet)
        total_evm_balance += balance
        print(f"Wallet: {wallet} - Balance: {balance:.4f} HYPE")
        current_run.append({"type": "evm", "wallet": wallet, "balance": balance})
    print("-------------------------")
    
    # Get HyperCore balances - only show HYPE
    print("\nCurrent HYPE Token Balances (HyperCore):")
    total_hypercore_hype = 0
    total_staked_hype = 0
    
    for wallet in wallets:
        hypercore_balances = get_hypercore_balance(wallet)
        hype_balance = 0
        if hypercore_balances:
            for balance in hypercore_balances:
                coin = balance.get("coin", "Unknown")
                if coin == "HYPE":
                    amount = float(balance.get("total", "0"))
                    hype_balance = amount
                    total_hypercore_hype += amount
                    print(f"Wallet: {wallet} - Balance: {amount:.4f} HYPE")
                
                # Still store all balances in the database
                current_run.append({
                    "type": "hypercore",
                    "wallet": wallet,
                    "coin": coin,
                    "balance": float(balance.get("total", "0"))
                })
            
            if hype_balance == 0:
                print(f"Wallet: {wallet} - No HYPE balance found")
        else:
            print(f"Wallet: {wallet} - No HyperCore balances found")
            
        # Check for staking balances
        staking_info = get_staking_balance(wallet)
        if staking_info and "delegated" in staking_info:
            delegated = float(staking_info.get("delegated", "0"))
            if delegated > 0:
                total_staked_hype += delegated
                print(f"Wallet: {wallet} - Staked: {delegated:.4f} HYPE")
                # Store staking info in the database
                current_run.append({
                    "type": "staking",
                    "wallet": wallet,
                    "balance": delegated
                })
    
    print("-------------------------")
    
    # Get current HYPE price
    hype_price = get_hype_price()
    
    # Show individual totals
    print(f"Total HYPE Balance (EVM): {total_evm_balance:.4f} HYPE")
    if hype_price:
        evm_usd_value = total_evm_balance * hype_price
        print(f"USD Value: ${evm_usd_value:.2f}")
    
    print(f"Total HYPE Balance (HyperCore): {total_hypercore_hype:.4f} HYPE")
    if hype_price:
        hypercore_usd_value = total_hypercore_hype * hype_price
        print(f"USD Value: ${hypercore_usd_value:.2f}")
    
    print(f"Total Staked HYPE: {total_staked_hype:.4f} HYPE")
    if hype_price:
        staked_usd_value = total_staked_hype * hype_price
        print(f"USD Value: ${staked_usd_value:.2f}")
    
    # Show combined total (including staked)
    combined_total = total_evm_balance + total_hypercore_hype + total_staked_hype
    print(f"\nCombined Total HYPE Balance (including staked): {combined_total:.4f} HYPE")
    if hype_price:
        combined_usd_value = combined_total * hype_price
        print(f"Combined USD Value: ${combined_usd_value:.2f} (HYPE price: ${hype_price:.4f})")
    else:
        print("Unable to fetch current HYPE price")
    
    # Clear old data and insert current balances into TinyDB
    db.truncate()
    db.insert_multiple(current_run)

if __name__ == '__main__':
    main()