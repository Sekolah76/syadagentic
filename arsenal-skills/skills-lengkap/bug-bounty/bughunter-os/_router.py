#!/usr/bin/env python3
"""
BugHunter OS — Auto-Router

Routes user queries to the right file(s) in the bughunter-os knowledge base.

Usage:
  python3 _router.py "reentrancy in lending protocol"
  python3 _router.py "audit AMM"
  python3 _router.py "build PoC for oracle manipulation"

Or interactive mode:
  python3 _router.py --interactive
"""

import os
import re
import sys
from collections import defaultdict
from pathlib import Path

SKILL_DIR = Path(__file__).parent


def scan_files():
    """Scan all .md files and extract metadata."""
    files_data = []
    for root, dirs, files in os.walk(SKILL_DIR):
        for f in files:
            if not f.endswith('.md') or f in ('INDEX.md', 'SKILL.md'):
                continue
            full_path = Path(root) / f
            rel_path = full_path.relative_to(SKILL_DIR)
            try:
                content = full_path.read_text(errors='ignore')
            except:
                continue

            m = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = m.group(1).strip() if m else f.replace('.md', '').replace('_', ' ').title()

            cat = str(rel_path).split('/')[0] if '/' in str(rel_path) else 'root'

            files_data.append({
                'path': str(rel_path),
                'title': title,
                'category': cat,
                'content_sample': content[:500].lower(),
            })
    return files_data


# Keyword → file category mapping
KEYWORD_MAP = {
    # Vulnerability classes
    'reentrancy': ['reentrancy', 'curve.md', 'attack-patterns-batch1-common/reentrancy'],
    'oracle': ['oracle', 'attack-patterns-batch1-common/oracle', 'attack-patterns-batch2-protocolspecific/Oracle'],
    'flash loan': ['flash loan', 'sandwich', 'beanstalk', 'flashloan'],
    'signature': ['signature', 'wormhole', 'nomad', 'replay'],
    'governance': ['governance', 'vote', 'proposal', 'quorum', 'timelock'],
    'bridge': ['bridge', 'cross-chain', 'wormhole', 'nomad', 'ronin', 'transit'],
    'proxy': ['proxy', 'upgrade', 'storage_collision', 'Upgradeability'],
    'access control': ['access', 'control', 'permission', 'role'],

    # Protocol types
    'amm': ['amm', 'swap', 'pool', 'liquidity', 'virtual_reserve'],
    'lending': ['lending', 'borrow', 'collateral', 'liquidation', 'paraspace', 'uwu', 'midas', 'hundred', 'sonne'],
    'liquid staking': ['liquid staking', 'restaking', 'lst', 'share_depeg'],
    'stablecoin': ['stablecoin', 'usdc', 'usdt', 'dai', 'depeg', 'redemption'],
    'vault': ['vault', 'yield_aggregator', 'strategy', 'harvest'],
    'perpetual': ['perpetual', 'perp', 'funding'],
    'option': ['option', 'greeks', 'expiry'],
    'nft': ['nft', 'marketplace', 'auction', 'paraspace'],
    'rwa': ['rwa', 'real world asset'],

    # ERC standards
    'erc20': ['erc20', 'fee_on_transfer', 'rebasing', 'permit'],
    'erc4626': ['erc4626', 'vault standard', 'share_inflation', 'donation_attack'],

    # Process
    'audit new': ['repository_classifier', 'protocol_detector', 'audit_planner'],
    'start audit': ['repository_classifier', 'protocol_detector', 'audit_planner'],
    'phase 1': ['bughunter-phase1'],
    'phase 2': ['bughunter-phase2'],
    'phase 3': ['bughunter-phase3'],
    'phase 4': ['bughunter-phase4'],
    'phase 5': ['bughunter-phase5'],
    'phase 6': ['bughunter-phase6'],
    'phase 7': ['bughunter-phase7', 'exploit_builder', 'poc_builder'],
    'phase 8': ['bughunter-phase8', 'report', 'quality_gate'],

    # Reporting
    'report': ['phase8', 'report_generator', 'report_template', 'orchestrator-batch5'],
    'poc': ['exploit_builder', 'poc_builder', 'phase7'],
    'severity': ['severity_engine', 'severity_classification', 'phase8'],
    'false positive': ['false_positive', 'consistency_checker', 'quality_gate', 'phase8'],

    # Specific exploits
    'wormhole': ['wormhole', 'signature'],
    'ronin': ['ronin', 'validator', 'bridge'],
    'nomad': ['nomad', 'message hash', 'bridge'],
    'curve': ['curve', 'reentrancy', 'stable swap'],
    'beanstalk': ['beanstalk', 'governance', 'flash loan'],
    'prisma': ['prisma', 'hook', 'lending'],
    'sonne': ['sonne', 'market manipulation', 'lending'],
}


def route_query(query, files_data):
    """Route a query to relevant files."""
    query_lower = query.lower()
    matches = []

    # Direct keyword matching
    for kw, patterns in KEYWORD_MAP.items():
        if kw in query_lower:
            for f in files_data:
                path_lower = f['path'].lower()
                title_lower = f['title'].lower()
                for p in patterns:
                    if p.lower() in path_lower or p.lower() in title_lower or p.lower() in f['content_sample']:
                        score = 10  # Direct keyword match
                        if kw in title_lower:
                            score += 5
                        if kw in path_lower:
                            score += 3
                        matches.append((score, f))
                        break

    # De-duplicate
    seen = set()
    unique_matches = []
    for score, f in sorted(matches, key=lambda x: -x[0]):
        if f['path'] not in seen:
            seen.add(f['path'])
            unique_matches.append((score, f))

    return unique_matches[:15]


def print_results(query, matches):
    """Print routed results."""
    print(f"\n🔍 Query: \"{query}\"\n")
    if not matches:
        print("❌ No matches. Try keywords like: reentrancy, oracle, flash loan, amm, lending, bridge, governance, etc.\n")
        return

    print(f"📂 {len(matches)} relevant file(s):\n")
    for i, (score, f) in enumerate(matches, 1):
        print(f"  [{i}] {f['path']}")
        print(f"      → {f['title']}")
        print(f"      (category: {f['category']}, score: {score})")
        print()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    files_data = scan_files()

    if sys.argv[1] == '--interactive' or sys.argv[1] == '-i':
        print("\n🤖 BugHunter OS Router (interactive mode)")
        print("Type 'quit' or 'exit' to stop\n")
        while True:
            try:
                query = input("🔍 Query: ").strip()
            except (EOFError, KeyboardInterrupt):
                break
            if not query or query.lower() in ('quit', 'exit', 'q'):
                break
            matches = route_query(query, files_data)
            print_results(query, matches)
    else:
        query = ' '.join(sys.argv[1:])
        matches = route_query(query, files_data)
        print_results(query, matches)


if __name__ == '__main__':
    main()
