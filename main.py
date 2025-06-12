import os
import json
import time
import threading
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

from engine import (
    token_scanner,
    paper_trader,
    wallet_scanner,
    pattern_extractor,
    pattern_predictor,
    self_learning,
)

from engine.mcp_scanner import MCPScanner

# Load config
with open("config.json") as f:
    config = json.load(f)

bot_token = config["telegram_bot_token"]
user_id = config["telegram_user_id"]
app = ApplicationBuilder().token(bot_token).build()

# Initialize MCPScanner
mcp = MCPScanner()
tracked_path = "engine/tracked_tokens.json"
if os.path.exists(tracked_path):
    with open(tracked_path, "r") as f:
        tracked = json.load(f)
        mcp.load_historical_clusters(tracked)

# Commands
async def start(update, context):
    if str(update.effective_user.id) != str(user_id):
        return
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="🤖 Bot started!"
    )

async def paperstatus(update, context):
    if str(update.effective_user.id) != str(user_id):
        return
    text = paper_trader.get_status()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

async def togglemode(update, context):
    if str(update.effective_user.id) != str(user_id):
        return
    mode = paper_trader.toggle_mode()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Paper mode is now: {mode.upper()}"
    )

async def sellnow(update, context):
    if str(update.effective_user.id) != str(user_id):
        return
    if len(context.args) != 1:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Usage: /sellnow <mint>"
        )
        return
    msg = paper_trader.force_sell(context.args[0])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

async def addtoken(update, context):
    if str(update.effective_user.id) != str(user_id):
        return
    if len(context.args) != 1:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Usage: /addtoken <mint>"
        )
        return

    mint = context.args[0]
    fake_token_data = {
        "mint": mint,
        "decimals": 9,
        "signature": "manual"
    }

    wallet_data = wallet_scanner.analyze_buyers(mint)
    fingerprint = pattern_extractor.extract_pattern_features(
        fake_token_data,
        wallet_data
    )

    if os.path.exists(tracked_path):
        with open(tracked_path, "r") as f:
            tracked = json.load(f)
    else:
        tracked = []

    tracked.append({
        "fingerprint": fingerprint,
        "wallets": wallet_data["buyers"],
        "price_change": 2.5  # assume 2.5x manually for now
    })

    with open(tracked_path, "w") as f:
        json.dump(tracked, f, indent=2)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🧠 Learned from {mint}."
    )

def handle_token_detected(token):
    wallet_data = wallet_scanner.analyze_buyers(token["mint"])
    fingerprint = pattern_extractor.extract_pattern_features(token, wallet_data)
    prediction = pattern_predictor.predict_match(fingerprint)

    confidence = prediction["confidence_score"]
    smart_count = wallet_data.get("smart_wallet_hits", 0)
    buyer_count = len(wallet_data.get("buyers", []))
    estimates = pattern_predictor.estimate_return_and_peak(smart_count, buyer_count)

    # MCP scoring handled by mcp_scanner
    mcp_data = mcp.score_wallets(wallet_data["buyers"])
    mcp_score = mcp_data["mcp_score"]
    cluster_strength = mcp_data["cluster_strength"]

    text = (
        f"🚨 New Token Detected\n"
        f"Mint: {token['mint']}\n"
        f"Confidence: {confidence}%\n"
        f"{estimates}\n"
        f"🧠 MCP Score: {mcp_score}\n"
        f"🔗 Cluster Strength: {cluster_strength}\n"
        f"Detected at {time.strftime('%Y-%m-%d %H:%M:%S')} UTC"
    )

    if confidence >= 96:
        text += "\n🔁 Paper trade triggered (4 SOL)"
        paper_trader.auto_trade(
            token["mint"],
            confidence,
            prediction.get("tag")
        )

    bot = Bot(token=bot_token)
    bot.send_message(chat_id=user_id, text=text)

def run_bot():
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("paperstatus", paperstatus))
    app.add_handler(CommandHandler("togglemode", togglemode))
    app.add_handler(CommandHandler("sellnow", sellnow))
    app.add_handler(CommandHandler("addtoken", addtoken))
    app.run_polling()

if __name__ == "__main__":
    print(f"Bot started at {time.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    
    # Start the self-learning loop in a separate thread
    threading.Thread(
        target=self_learning.run_self_learning_loop,
        daemon=True
    ).start()

    # Start the token scanner thread
    threading.Thread(
        target=token_scanner.run_scanner,
        args=(handle_token_detected,),
        daemon=True
    ).start()

    # Run the bot
    run_bot()