import networkx as nx
from collections import defaultdict

# This is a placeholder for a real wallet interaction graph
# In production this would be built from prior transactions or token co-buys

class MCPScanner:
    def __init__(self):
        self.graph = nx.Graph()
        self.wallet_success_count = defaultdict(int)

    def load_historical_clusters(self, tracked_tokens):
        for entry in tracked_tokens:
            wallets = entry.get("wallets", [])
            for i in range(len(wallets)):
                for j in range(i + 1, len(wallets)):
                    self.graph.add_edge(wallets[i], wallets[j])
            for w in wallets:
                self.wallet_success_count[w] += 1

    def score_wallets(self, buyers):
        """Score based on how connected each buyer is to known successful wallets"""
        score = 0
        cluster_strength = 0
        seen = set()

        for wallet in buyers:
            if wallet not in self.graph:
                continue
            neighbors = list(self.graph.neighbors(wallet))
            hits = sum(1 for n in neighbors if n in buyers and n not in seen)
            cluster_strength += hits
            seen.update(neighbors)

            if self.wallet_success_count[wallet] >= 2:
                score += 1

        return {
            "mcp_score": score,
            "cluster_strength": cluster_strength,
            "connected_wallets": list(seen)
        }
