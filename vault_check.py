#!/usr/bin/env python3
"""
Hyperliquid Vault Monitor — GitHub Actions version.
Sends results via Telegram bot.
"""
import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone

VAULTS = {
    "Systemic HyperGrowth": "0xd6e56265890b76413d1d527eb9b75e334c0c5b42",
    "Ultron": "0x45e7014f092c5f9c39482caec131346f13ac5e73",
    "Growi HF": "0x1e37a337ed460039d1b15bd3bc489de789768d5e",
    "drkmttr": "0xc179e03922afe8fa9533d3f896338b9fb87ce0c8",
}

API_URL = "https://api.hyperliquid.xyz/info"

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def fetch_vault(address):
    data = json.dumps({"type": "vaultDetails", "vaultAddress": address}).encode()
    req = urllib.request.Request(API_URL, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"error": str(e)}


def format_vault(name, details):
    if "error" in details:
        return f"❌ {name}: API error — {details['error']}"

    apr = round(float(details.get("apr", 0) or 0) * 100, 2)
    closed = details.get("isClosed", True)
    n_followers = len(details.get("followers", []))

    portfolio = details.get("portfolio", [])
    hist = portfolio[0][1].get("accountValueHistory", []) if portfolio else []
    if hist:
        latest = float(hist[-1][1])
        first = float(hist[0][1])
        day_change = round((latest - first) / first * 100, 2)
        tvl_str = f"${latest:,.0f}"
    else:
        tvl_str = "?"
        day_change = 0

    if closed:
        return f"🔴 {name}: ЗАКРЫТ"
    
    icon = "🟢" if day_change >= 0 else "🔴"
    return (
        f"{icon} {name}\n"
        f"   TVL: {tvl_str} | APR: {apr}% | 24ч: {day_change:+.2f}%\n"
        f"   👥 {n_followers} фолловеров"
    )


def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️  TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = json.dumps({
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": True,
    }).encode()
    req = urllib.request.Request(url, data=payload,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("ok"):
                print("✅ Telegram delivered")
            else:
                print(f"❌ Telegram error: {result}")
    except Exception as e:
        print(f"❌ Telegram send failed: {e}")


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [f"📊 <b>Hyperliquid Vaults</b> — {now}", ""]

    any_change = False
    for name, addr in VAULTS.items():
        details = fetch_vault(addr)
        report = format_vault(name, details)
        lines.append(report)
        lines.append("")

    text = "\n".join(lines)
    print(text)
    send_telegram(text)


if __name__ == "__main__":
    main()
