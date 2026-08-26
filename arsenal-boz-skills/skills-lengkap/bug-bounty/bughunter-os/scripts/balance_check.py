#!/usr/bin/env python3
# Practical bridge balance verification for exploit planning
# Usage: python3 balance_check.py <bridge_address> <network>

import sys, json, os
from web3 import Web3

def load_abi(file_path):
    """Load ABI from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: ABI file {file_path} not found")
        return []

def get_rpc_url(network):
    """Get RPC URL for network"""
    rpc_urls = {
        "ethereum": "https://mainnet.infura.io/v3/YOUR_KEY",
        "bsc": "https://bsc-dataseed1.binance.org/",
        "polygon": "https://polygon-mainnet.infura.io/v3/YOUR_KEY",
        "arbitrum": "https://arb1.arbitrum.io/rpc",
        "optimism": "https://mainnet.optimism.io",
        "base": "https://mainnet.base.org"
    }
    return rpc_urls.get(network.lower(), rpc_urls["ethereum"])

def verify_bridge_balances(bridge_address, network="ethereum", token_addresses=None):
    """
    Verify economic state of bridge contract
    Returns: Dictionary with balance information and value calculations
    """
    # Setup Web3 connection
    rpc_url = get_rpc_url(network)
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    
    print(f"Connecting to {network} network...")
    print(f"Connecting to {bridge_address}...")
    
    results = {
        "contract": bridge_address,
        "network": network,
        "timestamp": w3.eth.get_block_number(),
        "balances": {},
        "economic_metrics": {}
    }
    
    # Check ETH/native token balance
    eth_balance = w3.eth.get_balance(bridge_address)
    results["balances"]["native"] = {
        "balance_raw": eth_balance,
        "balance_ether": w3.from_wei(eth_balance, 'ether'),
        "token_symbol": "ETH"
    }
    
    # Check ERC20 token balances if addresses provided
    if token_addresses:
        erc20_abi = load_abi("abis/erc20_abi.json")
        if erc20_abi:
            for token_addr in token_addresses:
                try:
                    token_contract = w3.eth.contract(address=token_addr, abi=erc20_abi)
                    
                    token_balances = {
                        "balance_raw": token_contract.functions.balanceOf(bridge_address).call(),
                        "symbol": token_contract.functions.symbol().call(),
                        "decimals": token_contract.functions.decimals().call(),
                        "balance_formatted": token_contract.functions.balanceOf(bridge_address).call() / (10 ** token_contract.functions.decimals().call())
                    }
                    
                    results["balances"][token_addr] = token_balances
                    print(f"✓ {token_contract.functions.symbol().call()}: {token_balances['balance_formatted']} tokens")
                    
                except Exception as e:
                    print(f"✗ Error checking token {token_addr}: {e}")
    
    # Calculate economic metrics
    total_eth_value = w3.from_wei(eth_balance, 'ether')
    total_token_value = sum(b["balance_formatted"] for b in results["balances"].values() if b["token_symbol"] != "ETH")
    
    results["economic_metrics"] = {
        "total_eth_value": total_eth_value,
        "total_token_value": total_token_value,
        "exploit_potential": calculate_exploit_potential(results["balances"]),
        "risk_level": assess_risk_level(results["balances"]),
        "recommended_attack_vectors": identify_attack_vectors(results["balances"])
    }
    
    return results

def calculate_exploit_potential(balances):
    """Calculate potential exploit value based on current balances"""
    potential = {"max_theoretical_loss": 0, "conservative_estimate": 0, "risk_factors": []}
    
    for token_type, balance in balances.items():
        if token_type == "native":
            # ETH balance can be 100% drained (ignoring gas)
            max_loss = balance["balance_ether"] * 0.95  # 95% (account for gas)
            conservative_loss = balance["balance_ether"] * 0.5  # 50% conservative
        else:
            # ERC20 tokens depend on attack vector
            max_loss = balance["balance_formatted"] * 0.95
            conservative_loss = balance["balance_formatted"] * 0.3
        
        potential["max_theoretical_loss"] += max_loss
        potential["conservative_estimate"] += conservative_loss
        
        if max_loss > 1000:  # Large balance flag
            potential["risk_factors"].append(f"HIGH_VALUE_{token_type}: ${max_loss:,.2f}")
    
    return potential

def assess_risk_level(balances):
    """Assess risk level based on current balance distribution"""
    total_value = sum(
        b["balance_formatted" if b.get("token_symbol") != "ETH" else "balance_ether"]
        for b in balances.values()
    )
    
    if total_value > 10000:
        return "CRITICAL"
    elif total_value > 1000:
        return "HIGH"
    elif total_value > 100:
        return "MEDIUM"
    else:
        return "LOW"

def identify_attack_vectors(balances):
    """Identify potential attack vectors based on current balance state"""
    vectors = []
    
    for token_type, balance in balances.items():
        if token_type == "native":
            eth_value = balance["balance_ether"]
            if eth_value > 1000:
                vectors.extend([
                    "FEE_MANIPULATION",
                    "BRIDGE_PAUSE_BYPASS", 
                    "WITHDRAWAL_PROOF_BYPASS"
                ])
            elif eth_value > 100:
                vectors.extend([
                    "WRAPPED_ASSET_DESYNC",
                    "ACCOUNTING_INVESTIGATION"
                ])
        else:
            token_value = balance["balance_formatted"]
            if token_value > 5000:
                vectors.extend([
                    "ASSET_INFLATION_ATTACK",
                    "RESERVE_IMBALANCE",
                    "TOKEN_MANIPULATION"
                ])
            elif token_value > 500:
                vectors.extend([
                    "FEE_EXPLOIT",
                    "ECONOMIC_ATTACK"
                ])
    
    # Remove duplicates and return
    return list(set(vectors))

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 balance_check.py <bridge_address> <network>")
        print("Example: python3 balance_check.py 0x1234567890123456789012345678901234567890 ethereum")
        print("\nAvailable networks: ethereum, bsc, polygon, arbitrum, optimism, base")
        sys.exit(1)
    
    bridge_address = sys.argv[1]
    network = sys.argv[2]
    
    # Known token addresses for common bridges (extend as needed)
    token_addresses = [
        "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",  # WETH on Ethereum
        "0x4e3Decbb2b2b013d9b5a67B5fF5F5F5F5F5F5F5F5"  # Example token
    ]
    
    try:
        results = verify_bridge_balances(bridge_address, network, token_addresses)
        
        print("\n" + "="*60)
        print("BRIDGE ECONOMIC STATE REPORT")
        print("="*60)
        print(f"Contract: {results['contract']}")
        print(f"Network: {results['network']}")
        print(f"Block: {results['timestamp']}")
        print("\nCURRENT BALANCES:")
        for token_type, balance in results["balances"].items():
            if token_type == "native":
                print(f"  ETH: {balance['balance_ether']:.4f} ETH")
            else:
                print(f"  {balance['symbol']}: {balance['balance_formatted']:.4f}")
        
        print(f"\nECONOMIC METRICS:")
        print(f"  Total Value: ${results['economic_metrics']['total_eth_value'] + results['economic_metrics']['total_token_value']:.2f}")
        print(f"  Risk Level: {results['economic_metrics']['risk_level']}")
        print(f"  Max Theoretical Loss: ${results['economic_metrics']['exploit_potential']['max_theoretical_loss']:.2f}")
        print(f"  Conservative Estimate: ${results['economic_metrics']['exploit_potential']['conservative_estimate']:.2f}")
        
        print(f"\nRECOMMENDED ATTACK VECTORS:")
        for vector in results['economic_metrics']['recommended_attack_vectors']:
            print(f"  • {vector}")
        
        print(f"\nRISK FACTORS:")
        for factor in results['economic_metrics']['exploit_potential']['risk_factors']:
            print(f"  • {factor}")
        
        # Save results to file
        with open(f"balance_report_{bridge_address[:10]}.json", 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nFull report saved to: balance_report_{bridge_address[:10]}.json")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()