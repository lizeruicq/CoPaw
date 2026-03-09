---
name: market_data
description: "Query real-time market prices for gold, global indices (NASDAQ-100, S&P 500, Dow Jones), ETFs, stocks, and commodities. Use this skill when the user asks about gold prices, stock market indices, ETF prices, or any financial market data."
metadata:
  {
    "copaw":
      {
        "emoji": "📈",
        "requires": {}
      }
  }
---

# Market Data Query

When the user asks about financial market data such as gold prices, stock indices, ETFs, or commodity prices, use the market data tools to fetch real-time information.

## When to Use

Use this skill when the user asks:
- "黄金价格多少？" / "Gold price?"
- "纳斯达克100/标普500/道琼斯怎么样？" / "How is NASDAQ/S&P 500/Dow Jones?"
- "大盘指数" / "Market indices"
- "某只股票代码（如 AAPL, TSLA, QQQ）的价格"
- "全球主要股市行情"

## Available Tools

### 1. get_asset_price
Fetch real-time price for a single asset (gold, index, ETF, or stock).

**Parameters:**
- `asset`: Asset name or symbol (e.g., "gold", "nasdaq", "QQQ", "AAPL")
- `include_details`: (optional) Set to true for open, high, low, previous close

**Supported shortcuts:**
| Asset | Shortcut Names | Symbol |
|-------|----------------|--------|
| Gold | "gold", "gld", "黄金" | GLD ETF |
| NASDAQ-100 | "nasdaq", "qqq", "ndx" | QQQ ETF |
| S&P 500 | "sp500", "spy" | SPY ETF |
| Dow Jones | "dow", "dia" | DIA ETF |
| Russell 2000 | "russell", "iwm" | IWM ETF |
| Hang Seng | "hsi" | ^HSI |
| Nikkei 225 | "n225", "nikkei" | ^N225 |
| VIX | "vix" | ^VIX |
| Silver | "silver" | SI=F |
| Oil | "oil" | CL=F |
| Bitcoin ETF | "bitcoin", "btc" | IBIT |

**Example tool calls:**
```json
{"asset": "gold"}
{"asset": "nasdaq", "include_details": true}
{"asset": "QQQ"}
```

### 2. get_gold_price
Fetch comprehensive gold price information from multiple sources (GLD ETF, IAU ETF).

**When to use:** When user specifically asks about gold prices or gold market.

**Example tool call:**
```json
{}
```

### 3. get_global_indices
Fetch a summary of major global stock indices.

**When to use:** When user asks about "全球股市", "world markets", "主要指数", or wants an overview of multiple markets.

**Example tool call:**
```json
{}
```

## How to Use

### For single asset query:
1. Identify the asset from user's question
2. Call `get_asset_price` with the asset name or symbol
3. Present the price, change, and percentage to the user
4. If user asks for "details" or "详细信息", set `include_details: true`

### For gold-specific query:
1. Call `get_gold_price`
2. Present both GLD and IAU ETF prices
3. Explain that GLD represents ~1/10 oz of gold per share

### For market overview:
1. Call `get_global_indices`
2. Present the table of major indices with their changes
3. Highlight notable movers (big gains/losses)

## Response Format

### For single asset:
```
📊 [Asset Name] ([Symbol])
💰 当前价格: $XXX.XX USD
📈 涨跌: +X.XX (+X.XX%)
（可选详细信息）
```

### For gold:
```
🥇 黄金价格行情
💰 黄金ETF (GLD): $XXX.XX
📈 黄金ETF (IAU): $XXX.XX
...
```

### For global indices:
```
🌍 全球主要指数行情
纳斯达克100 ETF 🇺🇸: $XXX.XX (X.XX%)
标普500 ETF 🇺🇸: $XXX.XX (X.XX%)
...
```

## Examples

**User:** "今天黄金价格怎么样？"
**Action:** Call `get_asset_price` with `asset: "gold"`

**User:** "纳斯达克和标普500现在多少点？"
**Action:** Call `get_asset_price` twice with `asset: "nasdaq"` and `asset: "sp500"`

**User:** "全球股市行情如何？"
**Action:** Call `get_global_indices`

**User:** "QQQ的详细价格信息"
**Action:** Call `get_asset_price` with `asset: "QQQ"`, `include_details: true`

## Notes

- Prices are delayed by 15 minutes for some exchanges (standard for free data tier)
- ETF prices are in USD unless otherwise noted
- Index values are in points (点)
- Gold ETFs (GLD, IAU) track gold price but have management fees and slight tracking differences
- For Chinese users, you can respond in Chinese with the data
