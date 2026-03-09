# -*- coding: utf-8 -*-
"""Market data tools using Finnhub API.

This module provides real-time prices for:
- Gold (XAU/USD, GLD ETF, GC futures)
- Global indices (NASDAQ-100, S&P 500, Dow Jones, etc.)
- Stocks and ETFs

Environment Variable:
    FINNHUB_API_KEY: Your Finnhub API key
"""
import logging
import os
from typing import Optional

import requests
from agentscope.message import TextBlock
from agentscope.tool import ToolResponse

logger = logging.getLogger(__name__)

# Symbol mappings for common assets
ASSET_MAP = {
    # Gold variants (free tier supports ETFs, not forex)
    "gold": {"symbol": "GLD", "name": "黄金ETF(SPDR)", "currency": "USD"},
    "gld": {"symbol": "GLD", "name": "SPDR黄金ETF", "currency": "USD"},
    "gc": {"symbol": "GC=F", "name": "COMEX黄金期货", "currency": "USD/盎司"},
    "iau": {"symbol": "IAU", "name": "iShares黄金信托", "currency": "USD"},

    # US Indices - ETFs
    "nasdaq": {"symbol": "QQQ", "name": "纳斯达克100 ETF", "currency": "USD"},
    "qqq": {"symbol": "QQQ", "name": "纳斯达克100 ETF", "currency": "USD"},
    "ndx": {"symbol": "QQQ", "name": "纳斯达克100 ETF", "currency": "USD"},
    "sp500": {"symbol": "SPY", "name": "标普500 ETF", "currency": "USD"},
    "spy": {"symbol": "SPY", "name": "标普500 ETF", "currency": "USD"},
    "dow": {"symbol": "DIA", "name": "道琼斯ETF", "currency": "USD"},
    "dia": {"symbol": "DIA", "name": "道琼斯ETF", "currency": "USD"},
    "russell": {"symbol": "IWM", "name": "罗素2000 ETF", "currency": "USD"},
    "iwm": {"symbol": "IWM", "name": "罗素2000 ETF", "currency": "USD"},

    # US Indices - Cash
    "^ixic": {"symbol": "^IXIC", "name": "纳斯达克综合指数", "currency": "点"},
    "^gspc": {"symbol": "^GSPC", "name": "标普500指数", "currency": "点"},
    "^dji": {"symbol": "^DJI", "name": "道琼斯工业指数", "currency": "点"},
    "^ndx": {"symbol": "^NDX", "name": "纳斯达克100指数", "currency": "点"},

    # Global Indices
    "hsi": {"symbol": "^HSI", "name": "恒生指数", "currency": "点"},
    "n225": {"symbol": "^N225", "name": "日经225", "currency": "点"},
    "ftse": {"symbol": "^FTSE", "name": "英国富时100", "currency": "点"},
    "dax": {"symbol": "^GDAXI", "name": "德国DAX指数", "currency": "点"},
    "cac": {"symbol": "^FCHI", "name": "法国CAC40", "currency": "点"},

    # Volatility
    "vix": {"symbol": "^VIX", "name": "VIX恐慌指数", "currency": "点"},

    # Commodities
    "silver": {"symbol": "SI=F", "name": "白银期货", "currency": "USD/盎司"},
    "oil": {"symbol": "CL=F", "name": "WTI原油期货", "currency": "USD/桶"},
    "brent": {"symbol": "BZ=F", "name": "布伦特原油期货", "currency": "USD/桶"},

    # Crypto ETFs
    "bitcoin": {"symbol": "IBIT", "name": "iShares比特币信托", "currency": "USD"},
    "ethereum": {"symbol": "ETHA", "name": "Franklin以太坊ETF", "currency": "USD"},
}


def _get_api_key() -> str:
    """Get API key from environment variable.

    Returns:
        API key from FINNHUB_API_KEY environment variable

    Raises:
        ValueError: If FINNHUB_API_KEY environment variable is not set
    """
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        raise ValueError(
            "FINNHUB_API_KEY environment variable is not set. "
            "Please set it with: export FINNHUB_API_KEY='your_api_key'"
        )
    return api_key


def _make_request(endpoint: str, params: dict = None) -> dict:
    """Make a request to Finnhub API."""
    api_key = _get_api_key()
    base_url = "https://finnhub.io/api/v1"

    params = params or {}
    params["token"] = api_key

    try:
        response = requests.get(
            f"{base_url}/{endpoint}",
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Finnhub API request failed: {e}")
        return {"error": str(e)}


def get_quote(symbol: str) -> dict:
    """Get real-time quote for a symbol.

    Args:
        symbol: Stock/ETF/Index symbol (e.g., 'AAPL', 'QQQ', 'GLD')

    Returns:
        Dict with price data
    """
    data = _make_request("quote", {"symbol": symbol})

    if "error" in data:
        return data

    return {
        "symbol": symbol,
        "current": data.get("c"),  # Current price
        "change": data.get("d"),   # Change
        "change_percent": data.get("dp"),  # Change percent
        "high": data.get("h"),     # High of the day
        "low": data.get("l"),      # Low of the day
        "open": data.get("o"),     # Open price
        "previous_close": data.get("pc"),  # Previous close
        "timestamp": data.get("t"),  # Timestamp
    }


def normalize_asset(asset: str) -> dict:
    """Normalize asset name to symbol info."""
    asset_lower = asset.lower().strip()

    # Check if it's in our map
    if asset_lower in ASSET_MAP:
        return ASSET_MAP[asset_lower]

    # Otherwise treat as direct symbol
    return {
        "symbol": asset.upper(),
        "name": asset.upper(),
        "currency": "USD"
    }


def _format_asset_price(asset: str, include_details: bool = False) -> str:
    """Internal function to format asset price."""
    # Handle Chinese input for gold
    if asset in ["黄金", "金子"]:
        asset = "gold"

    # Get symbol info
    info = normalize_asset(asset)
    symbol = info["symbol"]
    name = info["name"]
    currency = info["currency"]

    # Fetch data
    data = get_quote(symbol)

    if "error" in data:
        return f"❌ 获取 {asset} 价格失败: {data['error']}"

    if data.get("current") is None:
        return f"❌ 无法获取 {asset} ({symbol}) 的价格数据"

    # Format output
    lines = [
        f"📊 {name} ({symbol})",
        f"💰 当前价格: {data['current']:,.2f} {currency}",
    ]

    # Add change with emoji
    change = data.get("change")
    change_pct = data.get("change_percent")

    if change is not None and change_pct is not None:
        emoji = "📈" if change >= 0 else "📉"
        lines.append(f"{emoji} 涨跌: {change:+.2f} ({change_pct:+.2f}%)")

    if include_details:
        if data.get("open"):
            lines.append(f"📊 开盘: {data['open']:,.2f}")
        if data.get("high"):
            lines.append(f"⬆️ 最高: {data['high']:,.2f}")
        if data.get("low"):
            lines.append(f"⬇️ 最低: {data['low']:,.2f}")
        if data.get("previous_close"):
            lines.append(f"📉 昨收: {data['previous_close']:,.2f}")

    return "\n".join(lines)


def get_asset_price(asset: str, include_details: bool = False) -> ToolResponse:
    """Get real-time price for gold or global indices.

    Use this tool when user asks about:
    - Gold prices (黄金)
    - Stock indices (纳斯达克, 标普, 道琼斯)
    - ETF prices
    - 全球宽基指数

    Args:
        asset: Asset name or symbol.
               Supported shortcuts:
               - 'gold', '黄金' -> 黄金现货
               - 'gld' -> 黄金ETF
               - 'nasdaq', 'qqq', 'ndx' -> 纳斯达克100
               - 'sp500', 'spy' -> 标普500
               - 'dow', 'dia' -> 道琼斯
               - 'hsi' -> 恒生指数
               - 'n225' -> 日经225
               - 'vix' -> 恐慌指数
               - Or any stock symbol like 'AAPL', 'TSLA'
        include_details: If True, include open, high, low, previous close

    Returns:
        ToolResponse with formatted price information
    """
    text = _format_asset_price(asset, include_details)
    return ToolResponse(
        content=[TextBlock(type="text", text=text)],
    )


def _format_gold_price() -> str:
    """Internal function to format gold price."""
    lines = ["🥇 黄金价格行情", "=" * 40]

    # GLD ETF (SPDR Gold Shares) - 1 share ≈ 1/10 oz of gold
    gld = get_quote("GLD")
    if gld.get("current"):
        lines.append(f"💰 黄金ETF (GLD): ${gld['current']:,.2f}")
        lines.append(f"   注: 1股GLD ≈ 1/10盎司黄金")
        if gld.get("change"):
            lines.append(f"   涨跌: {gld['change']:+.2f} ({gld['change_percent']:+.2f}%)")

    # IAU ETF (iShares Gold Trust) - 1 share ≈ 1/100 oz of gold
    iau = get_quote("IAU")
    if iau.get("current"):
        lines.append(f"📈 黄金ETF (IAU): ${iau['current']:,.2f}")
        lines.append(f"   注: 1股IAU ≈ 1/100盎司黄金")

    # Gold futures (may require higher tier)
    gc = get_quote("GC=F")
    if gc.get("current") and "error" not in str(gc.get("current", "")).lower():
        lines.append(f"📊 黄金期货 (GC): ${gc['current']:,.2f}/盎司")

    return "\n".join(lines)


def get_gold_price() -> ToolResponse:
    """Get current gold price in multiple formats.

    Returns:
        ToolResponse with gold price information from multiple sources
    """
    text = _format_gold_price()
    return ToolResponse(
        content=[TextBlock(type="text", text=text)],
    )


def _format_global_indices() -> str:
    """Internal function to format global indices."""
    indices = [
        ("QQQ", "纳斯达克100 ETF 🇺🇸"),
        ("SPY", "标普500 ETF 🇺🇸"),
        ("DIA", "道琼斯ETF 🇺🇸"),
        ("^VIX", "VIX恐慌指数 😰"),
        ("^HSI", "恒生指数 🇭🇰"),
        ("^N225", "日经225 🇯🇵"),
    ]

    lines = ["🌍 全球主要指数行情", "=" * 50]
    lines.append(f"{'指数':<15} {'价格':>12} {'涨跌':>12}")
    lines.append("-" * 50)

    for symbol, name in indices:
        data = get_quote(symbol)
        if data.get("current"):
            price = f"{data['current']:,.2f}"
            if data.get("change_percent") is not None:
                change = f"{data['change_percent']:+.2f}%"
                lines.append(f"{name:<15} {price:>12} {change:>12}")
            else:
                lines.append(f"{name:<15} {price:>12} {'N/A':>12}")

    return "\n".join(lines)


def get_global_indices() -> ToolResponse:
    """Get major global indices summary.

    Returns:
        ToolResponse with summary of major global stock indices
    """
    text = _format_global_indices()
    return ToolResponse(
        content=[TextBlock(type="text", text=text)],
    )


# For CoPaw tool registration
if __name__ == "__main__":
    # Test the functions
    import asyncio

    async def test():
        result = get_asset_price("gold")
        print(result)

    asyncio.run(test())
