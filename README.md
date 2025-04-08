# Hyperliquid Wallet Watcher

A Python utility to monitor HYPE token balances across multiple wallets on both Hyperliquid EVM and HyperCore L1.

## Overview

This tool tracks HYPE token balances for a configured list of wallets across:
- Hyperliquid EVM native balances
- HyperCore balances
- Delegated staking positions

It fetches real-time data from Hyperliquid's RPC and API endpoints, calculates total holdings, and displays current USD value using Pyth oracle price data.

## Features

- Multi-wallet monitoring across multiple Hyperliquid chains
- Tracks EVM native HYPE balance
- Tracks HyperCore HYPE balance
- Tracks delegated staking positions
- Stores historical balance data using TinyDB
- Fetches current HYPE/USD price using Pyth oracle
- Calculates combined total holdings and USD value

## Requirements

- Python 3.6+
- `requests` library
- `tinydb` library

## Installation

1. Clone this repository:
```
git clone https://github.com/anonmarkets/hl-wallet-watcher.git
cd hl-wallet-watcher
```

2. Install dependencies:
```
pip install requests tinydb
```

## Usage

1. Edit the `wallets` list in `main.py` to include your wallet addresses
2. Run the script:
```
python main.py
```

## Output

The script will display:
- Previous balances (if any)
- Current EVM HYPE balances for each wallet
- Current HyperCore HYPE balances for each wallet
- Staked HYPE amounts for each wallet
- Total balances for each system (EVM, HyperCore, Staking)
- Combined total balance with USD value

## Data Storage

Balance data is stored in `balances.json` using TinyDB. Each run updates this file with the latest balances.

## API Endpoints

The script uses the following API endpoints:
- Hyperliquid RPC: https://rpc.hyperliquid.xyz/evm
- Hyperliquid API: https://api.hyperliquid.xyz/info
- Pyth Oracle (via Hermes API): https://hermes.pyth.network/v2/updates/price/latest

## License

GNU GPLv3

## Contact
X: https://x.com/anonmarkets

- Hyperliquid: https://app.hyperliquid.xyz/join/ANONMARKETS
- pvp.trade: https://pvp.trade/join/xiere1
- Donation: 0xB2cef143Bea4FF180Fe2831932B4da04c3259333