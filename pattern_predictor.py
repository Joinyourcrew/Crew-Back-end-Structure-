import math
import random

# Sample historical data format (you can replace with real pump data)
historical_tokens = [
    {
        "smart_wallets": 3,
        "total_buyers": 20,
        "return_multiple": 2.7,
        "time_to_peak": 22  # in minutes
    },
    {
        "smart_wallets": 5,
        "total_buyers": 18,
        "return_multiple": 4.1,
        "time_to_peak": 15
    },
    {
        "smart_wallets": 2,
        "total_buyers": 30,
        "return_multiple": 1.8,
        "time_to_peak": 35
    },
    {
        "smart_wallets": 6,
        "total_buyers": 19,
        "return_multiple": 3.5,
        "time_to_peak": 18
    }
]

def estimate_return_and_peak(smart_count, buyer_count):
    if buyer_count == 0:
        return "❌ Not enough data to estimate."

    similarities = []

    for token in historical_tokens:
        score = 0
        score -= abs(token["smart_wallets"] - smart_count) * 2
        score -= abs(token["total_buyers"] - buyer_count)
        similarities.append((score, token))

    similarities.sort(reverse=True, key=lambda x: x[0])
    top = similarities[:3]

    avg_return = sum([t["return_multiple"] for _, t in top]) / len(top)
    avg_time = sum([t["time_to_peak"] for _, t in top]) / len(top)

    return f"📈 Est. Return: {avg_return:.1f}x\n⏱ Est. Peak: {int(avg_time)} min"
