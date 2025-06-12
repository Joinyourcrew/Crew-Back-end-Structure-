def extract_pattern_features(token_data, wallet_analysis):
    """
    Converts token + wallet data into a normalized feature vector.
    Used to compare patterns between tokens.
    """

    # Token basics
    decimals = token_data.get("decimals", 0)
    mint = token_data.get("mint", "")
    signature = token_data.get("signature", "")

    # Wallet stats
    buyers = wallet_analysis.get("buyers", [])
    smart_hits = wallet_analysis.get("smart_wallet_hits", 0)
    whale_hits = wallet_analysis.get("whale_hits", 0)
    bundle = 1 if wallet_analysis.get("bundle_detected") else 0

    buyer_count = len(buyers)
    avg_amount = sum([b["amount"] for b in buyers]) / max(buyer_count, 1)
    whale_ratio = whale_hits / max(buyer_count, 1)
    smart_ratio = smart_hits / max(buyer_count, 1)

    # Extract early-time activity (first 30 minutes windowed)
    bucket_counts = {}
    for b in buyers:
        time = b["blocktime"]
        if time != "N/A":
            bucket = time[:16]  # 'YYYY-MM-DD HH:MM'
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1

    active_buckets = len(bucket_counts)
    max_burst = max(bucket_counts.values(), default=0)

    return {
        "mint": mint,
        "signature": signature,
        "buyer_count": buyer_count,
        "smart_wallet_ratio": round(smart_ratio, 3),
        "whale_ratio": round(whale_ratio, 3),
        "avg_amount": avg_amount,
        "bundle_detected": bundle,
        "burst_window_count": active_buckets,
        "burst_max": max_burst,
        "decimals": decimals
    }
