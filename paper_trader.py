import json
import os
import time

PAPER_FILE = "engine/paper_state.json"
DEFAULT_BALANCE = 10.0

paper_state = {
    "mode": "paper",
    "balance": DEFAULT_BALANCE,
    "positions": {},
    "history": []
}


def save_state():
    with open(PAPER_FILE, "w") as f:
        json.dump(paper_state, f, indent=2)


def load_state():
    global paper_state
    if os.path.exists(PAPER_FILE):
        try:
            with open(PAPER_FILE, "r") as f:
                paper_state = json.load(f)
        except:
            reset_state()
    else:
        reset_state()


def reset_state():
    global paper_state
    paper_state = {
        "mode": "paper",
        "balance": DEFAULT_BALANCE,
        "positions": {},
        "history": []
    }
    save_state()


def toggle_mode():
    load_state()
    if paper_state["mode"] == "paper":
        paper_state["mode"] = "off"
    else:
        reset_state()
    save_state()
    return paper_state["mode"]


def get_status():
    load_state()
    pos = paper_state["positions"]
    summary = "\n".join([f"{t}: {d['amount']} SOL (score: {d['score']})" for t, d in pos.items()]) or "None"
    return (
        f"📊 Paper Trading Mode: {paper_state['mode']}\n"
        f"💰 Balance: {round(paper_state['balance'], 2)} SOL\n"
        f"📦 Positions:\n{summary}"
    )


def get_buy_amount(score):
    if score >= 96:
        return 4
    elif score >= 90:
        return 3
    elif score >= 80:
        return 2
    else:
        return 1


def auto_trade(token, score, prediction=None):
    load_state()
    if paper_state["mode"] != "paper":
        return False

    if token in paper_state["positions"]:
        return False

    amount = get_buy_amount(score)
    if paper_state["balance"] < amount:
        return False

    paper_state["balance"] -= amount
    paper_state["positions"][token] = {
        "amount": amount,
        "score": score,
        "buy_time": time.time(),
        "prediction": prediction or ""
    }
    save_state()
    return True


def force_sell(token):
    load_state()
    if token not in paper_state["positions"]:
        return f"⚠️ No active position in {token}."

    pos = paper_state["positions"].pop(token)
    amount = pos["amount"]
    gain = amount * 0.5  # simulate 50% profit
    final_amount = amount + gain
    paper_state["balance"] += final_amount

    paper_state["history"].append({
        "token": token,
        "amount": final_amount,
        "sold_at": time.time(),
        "original_amount": amount,
        "gain": gain
    })
    save_state()
    return f"✅ Sold {token} for {final_amount:.2f} SOL (paper, +50%)."
