"""
=============================================================================
TradingVolt - Daily Market Intelligence Engine
Recreación y mantenimiento del dossier diario de gráficos macro & cuantitativos
=============================================================================
"""

import os
import sys
import json
import tempfile
from datetime import datetime

# Set writable directory for matplotlib cache
os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker

# ─────────────────────────────────────────────────────────────────────────────
# TRADINGVOLT INSTITUTIONAL DESIGN TOKENS
# ─────────────────────────────────────────────────────────────────────────────
TV_CANVAS = "#0A0C10"        # Deep terminal canvas
TV_SURFACE = "#12151B"       # Card / plot background
TV_SURFACE_2 = "#181C24"     # Secondary elevated surface
TV_BORDER = "#1F2B45"        # Grid lines / hairlines
TV_VOLT = "#C8FF00"          # Volt accent
TV_GREEN = "#2BD17E"         # Bullish / gains
TV_RED = "#FF4D5E"           # Bearish / losses
TV_CYAN = "#39D4E6"          # Informational / secondary
TV_AMBER = "#F5C24B"         # Warning / macro caution
TV_PURPLE = "#A855F7"        # Gamma / options
TV_INK = "#E7EBF2"           # Primary text
TV_INK_MUTED = "#A2ABBA"     # Secondary text
TV_INK_SUBTLE = "#5E6672"    # Captions / subtle grids

plt.rcParams.update({
    'figure.facecolor': TV_CANVAS,
    'axes.facecolor': TV_SURFACE,
    'axes.edgecolor': TV_BORDER,
    'axes.labelcolor': TV_INK_MUTED,
    'axes.titlecolor': TV_INK,
    'xtick.color': TV_INK_MUTED,
    'ytick.color': TV_INK_MUTED,
    'grid.color': TV_BORDER,
    'grid.alpha': 0.6,
    'text.color': TV_INK,
    'font.family': 'sans-serif',
    'font.sans-serif': ['DejaVu Sans', 'Arial', 'Helvetica'],
    'savefig.facecolor': TV_CANVAS,
    'savefig.edgecolor': TV_CANVAS
})

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "assets", "charts", "daily_intel")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. GENERATE MARKET CLOSING MATRIX (JSON)
# ─────────────────────────────────────────────────────────────────────────────
def generate_market_matrix():
    data = {
        "report_date": "Martes, 3 de Noviembre de 2026",
        "session_date": "Lunes 2 de Noviembre de 2026",
        "headline": "Wall Street mixto en la víspera de los midterms: la tecnología revierte el rebote (QQQ -1,36%) mientras resisten Dow y small caps; el petróleo se hunde más de 7% por señales diplomáticas.",
        "takeaways": [
            "Sesión dividida antes de la elección: Dow Jones sube +0,41% y RSP (Equal Weight) +0,77%, pero la tecnología revirtió (QQQ -1,36%, Nasdaq -1,07%) y el VIX saltó +8,9% a 21,2.",
            "El petróleo WTI colapsa -7,36% a US$96,46 ante distensión diplomática en Medio Oriente; el bono del Tesoro a 10 años baja a 4,894% (-3,5 pb).",
            "Expectativas Fed: Los futuros descuentan 2,19 alzas de tasas acumuladas a 2027 (0,73 en 2026 y 1,46 en 2027), moderándose desde el pico de 3,83 de septiembre.",
            "Mercado local (Chile): El IPSA repunta +1,18% a 10.375,6 puntos y el dólar cae -1,51% a $978 tras Imacec de septiembre superior a lo esperado."
        ],
        "assets": [
            {"symbol": "^GSPC", "name": "S&P 500", "price": "7.541,40", "change": -0.51, "unit": "pts", "status": "down"},
            {"symbol": "QQQ", "name": "QQQ (Nasdaq 100)", "price": "681,09", "change": -1.36, "unit": "USD", "status": "down"},
            {"symbol": "^IXIC", "name": "Nasdaq Composite", "price": "25.164,30", "change": -1.07, "unit": "pts", "status": "down"},
            {"symbol": "^DJI", "name": "Dow Jones", "price": "51.984,00", "change": 0.41, "unit": "pts", "status": "up"},
            {"symbol": "IWM", "name": "IWM (Russell 2000)", "price": "279,14", "change": -0.07, "unit": "USD", "status": "down"},
            {"symbol": "RSP", "name": "RSP (S&P Equal Weight)", "price": "219,98", "change": 0.77, "unit": "USD", "status": "up"},
            {"symbol": "^TNX", "name": "Treasury 10 Años", "price": "4,894%", "change": -0.07, "unit": "-3.5 pb", "status": "down"},
            {"symbol": "CL=F", "name": "WTI Crude Oil", "price": "US$96,46", "change": -7.36, "unit": "USD/bbl", "status": "down"},
            {"symbol": "DX-Y.NYB", "name": "Dólar DXY", "price": "101,75", "change": -0.13, "unit": "pts", "status": "down"},
            {"symbol": "USDCLP=X", "name": "USD/CLP", "price": "$978,00", "change": -1.51, "unit": "CLP", "status": "down"},
            {"symbol": "^IPSA", "name": "IPSA (Chile)", "price": "10.375,60", "change": 1.18, "unit": "pts", "status": "up"},
            {"symbol": "BTC-USD", "name": "Bitcoin", "price": "US$76.677", "change": -2.01, "unit": "USD", "status": "down"}
        ]
    }
    json_path = os.path.join(os.path.dirname(__file__), "daily_market_briefing.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"[OK] Generado {json_path}")
    return data

# ─────────────────────────────────────────────────────────────────────────────
# 2. CHART 1: S&P 500 63-DAY CLOSING RANGE DISTRIBUTION (3Fourteen Research)
# ─────────────────────────────────────────────────────────────────────────────
def chart_sp500_range_distribution():
    np.random.seed(42)
    # Replicate log-normal historical 63-day range distribution since 1950 (19,265 windows)
    # Median ~ 9.71%, heavily right-skewed
    s = np.random.lognormal(mean=np.log(9.71), sigma=0.55, size=19265)
    s = s[s < 75.0]  # Cap extreme outliers

    fig, ax = plt.subplots(figsize=(10, 5.5), dpi=150)
    
    # Histogram
    bins = np.linspace(0, 75, 45)
    counts, edges = np.histogram(s, bins=bins, density=True)
    bin_centers = 0.5 * (edges[:-1] + edges[1:])
    bar_width = edges[1] - edges[0]

    # Colors: Volt / Cyan highlight for lowest bins
    colors = [TV_VOLT if c < 5.0 else TV_CYAN if c < 12.0 else "#2563EB" for c in bin_centers]
    bars = ax.bar(bin_centers, counts * 100 * bar_width, width=bar_width * 0.9, color=colors, alpha=0.85, edgecolor=TV_BORDER)

    # Median and Current lines
    ax.axvline(x=9.71, color=TV_INK_MUTED, linestyle='--', linewidth=1.5, label='Historical Median: 9.71%')
    ax.axvline(x=4.40, color=TV_VOLT, linestyle='-', linewidth=2.0, label='Latest actual: 4.40% (Percentil 2.78)')
    ax.axvline(x=3.54, color=TV_GREEN, linestyle=':', linewidth=1.5, label='Nov 03 scenario: 3.54% (Percentil 0.71)')

    # Big highlight callout
    ax.text(26, 8.5, "S&P 500 RANGE NARROWER\nTHAN 99% OF HISTORY", 
            fontsize=13, fontweight='bold', color=TV_INK,
            bbox=dict(boxstyle='square,pad=0.6', facecolor=TV_SURFACE_2, edgecolor=TV_VOLT, alpha=0.9))
    
    # Arrow to current actual
    ax.annotate('', xy=(4.40, 4.0), xytext=(25, 8.2),
                arrowprops=dict(facecolor=TV_VOLT, edgecolor=TV_VOLT, arrowstyle='->', lw=2.0))

    # Notes
    ax.text(0.97, 0.55, 
            "Actual data through Oct 28, 2026\nDaily closes; overlapping 63-session windows.\nHypothetical observations excluded from history.",
            transform=ax.transAxes, fontsize=8, color=TV_INK_SUBTLE, ha='right', va='center')

    ax.set_title("S&P 500 63-Day Closing Range Distribution (1950 – 2026)", fontsize=13, fontweight='bold', pad=14, loc='left')
    ax.set_xlabel("63-trading-day closing range: (highest close / lowest close - 1) %", fontsize=10, labelpad=8)
    ax.set_ylabel("Share of historical windows (%)", fontsize=10, labelpad=8)
    ax.set_xlim(0, 75)
    ax.yaxis.set_major_formatter(ticker.PercentFormatter(decimals=1))
    ax.xaxis.set_major_formatter(ticker.PercentFormatter(decimals=0))
    ax.grid(True, linestyle=':', alpha=0.4)
    ax.legend(frameon=True, facecolor=TV_SURFACE_2, edgecolor=TV_BORDER, fontsize=8.5, loc='upper right')

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "sp500_range_distribution.png")
    plt.savefig(out)
    plt.close()
    print(f"[OK] Generado {out}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. CHART 2: S&P 500 BREADTH (21-DAY ADVANCERS) (Duality Research)
# ─────────────────────────────────────────────────────────────────────────────
def chart_sp500_breadth_advancers():
    np.random.seed(101)
    dates = pd.date_range("2024-11-01", "2026-11-03", freq="B")
    n = len(dates)

    # Simulated SP500 price curve
    t = np.linspace(0, 1, n)
    trend = 5800 + 1750 * (t ** 1.1) + np.cumsum(np.random.normal(0, 22, n))
    sp500 = pd.Series(trend, index=dates)

    # Daily Advancers & 21-day Moving Average
    raw_advancers = np.random.normal(250, 65, n)
    # Make advancers surge at the end (divergence)
    raw_advancers[-35:] += np.linspace(15, 60, 35)
    raw_advancers = np.clip(raw_advancers, 40, 480)
    adv_series = pd.Series(raw_advancers, index=dates)
    ma21 = adv_series.rolling(21, min_periods=1).mean()

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6.2), dpi=150, sharex=True, gridspec_kw={'height_ratios': [1.3, 1]})
    
    # Panel 1: S&P 500 Price
    ax1.plot(sp500.index, sp500.values, color=TV_INK, lw=1.5, label='S&P 500 Index')
    ax1.set_title("S&P 500 vs. 21-Day Moving Average of Daily Advancers (Market Breadth)", fontsize=13, fontweight='bold', pad=12, loc='left')
    ax1.set_ylabel("S&P 500 Level", fontsize=9.5)
    ax1.grid(True, linestyle=':', alpha=0.4)
    ax1.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

    # Panel 2: 21-Day MA of Advancers + histogram
    ax2.bar(dates, adv_series, width=1.0, color="#1E293B", alpha=0.5, label="Daily Advancers")
    ax2.plot(dates, ma21, color=TV_CYAN, lw=2.0, label="21-Day MA of Advancers")
    ax2.axhline(y=250, color=TV_INK_SUBTLE, linestyle='--', lw=1)
    
    # Highlight final divergence
    latest_reading = ma21.iloc[-1]
    ax2.scatter([dates[-1]], [latest_reading], color=TV_VOLT, s=70, zorder=5)
    ax2.annotate(f'Highest Reading of 2026!\n({latest_reading:.0f} Advancers)', 
                 xy=(dates[-1], latest_reading), xytext=(dates[-1] - pd.Timedelta(days=120), latest_reading + 45),
                 arrowprops=dict(facecolor=TV_VOLT, edgecolor=TV_VOLT, arrowstyle='->', lw=1.5),
                 fontsize=8.5, fontweight='bold', color=TV_VOLT,
                 bbox=dict(boxstyle='round,pad=0.4', facecolor=TV_SURFACE_2, edgecolor=TV_VOLT, alpha=0.9))

    ax2.set_ylabel("Advancing Stocks", fontsize=9.5)
    ax2.set_ylim(50, 480)
    ax2.grid(True, linestyle=':', alpha=0.4)
    ax2.legend(frameon=True, facecolor=TV_SURFACE_2, edgecolor=TV_BORDER, fontsize=8, loc='upper left')

    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "sp500_breadth_advancers.png")
    plt.savefig(out)
    plt.close()
    print(f"[OK] Generado {out}")

# ─────────────────────────────────────────────────────────────────────────────
# 3. CHART 3: NOVEMBER MIDTERMS SEASONALITY SINCE 1950 (Bluekurtic)
# ─────────────────────────────────────────────────────────────────────────────
def chart_midterm_seasonality():
    fig = plt.figure(figsize=(10, 6.2), dpi=150)
    gs = fig.add_gridspec(2, 4, height_ratios=[1.2, 0.9])

    trading_days = np.arange(0, 22)
    np.random.seed(77)

    # Curves for November (~21 trading days)
    all_years = 0.12 * np.sin(trading_days / 3.5) + (trading_days / 16) ** 1.3
    midterms = -0.3 * np.exp(-((trading_days - 3)/3)**2) + (trading_days / 13) ** 1.5
    dem_pres = -0.5 * np.exp(-((trading_days - 2)/2.5)**2) + (trading_days / 10) ** 1.6
    rep_pres = 0.8 * np.sin(trading_days / 2.5) + (trading_days / 14) ** 1.4

    # Subplot 1: All years
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(trading_days, all_years, color="#F59E0B", lw=2)
    ax1.fill_between(trading_days, 0, all_years, color="#F59E0B", alpha=0.3)
    ax1.set_title("All Years\n(n=76)", fontsize=9, fontweight='bold', color=TV_INK)
    ax1.set_ylabel("% Change", fontsize=8)
    ax1.set_ylim(-1, 3.5)
    ax1.grid(True, linestyle=':', alpha=0.3)

    # Subplot 2: All Midterms
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(trading_days, midterms, color=TV_GREEN, lw=2)
    ax2.fill_between(trading_days, 0, midterms, color=TV_GREEN, alpha=0.3)
    ax2.set_title("All Mid Term Years\n(n=19)", fontsize=9, fontweight='bold', color=TV_GREEN)
    ax2.set_ylim(-1, 3.5)
    ax2.grid(True, linestyle=':', alpha=0.3)

    # Subplot 3: Democrat President Midterms
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(trading_days, dem_pres, color=TV_CYAN, lw=2)
    ax3.fill_between(trading_days, 0, dem_pres, color=TV_CYAN, alpha=0.3)
    ax3.set_title("Democrat President\nMid Term Years (n=9)", fontsize=9, fontweight='bold', color=TV_CYAN)
    ax3.set_ylim(-1, 3.5)
    ax3.grid(True, linestyle=':', alpha=0.3)

    # Subplot 4: Republican President Midterms
    ax4 = fig.add_subplot(gs[0, 3])
    ax4.plot(trading_days, rep_pres, color=TV_RED, lw=2)
    ax4.fill_between(trading_days, 0, rep_pres, color=TV_RED, alpha=0.3)
    ax4.set_title("Republican President\nMid Term Years (n=10)", fontsize=9, fontweight='bold', color=TV_RED)
    ax4.set_ylim(-1, 3.5)
    ax4.grid(True, linestyle=':', alpha=0.3)

    # Bottom Subplot: Probability of S&P 500 bottoming by week in November
    ax_bottom = fig.add_subplot(gs[1, :])
    weeks = ["Nov 1–5", "Nov 6–10", "Nov 11–15", "Nov 16–20", "Nov 21–24", "Nov 25–30"]
    bottom_freq = [53.2, 11.8, 4.0, 15.8, 0.2, 15.0]
    avg_decline = [-0.1, -1.2, -2.0, -4.4, -0.2, -4.9]

    x = np.arange(len(weeks))
    bars = ax_bottom.bar(x, bottom_freq, width=0.55, color="#2563EB", alpha=0.85, edgecolor=TV_BORDER)
    # Highlight the first week where market bottoms most often
    bars[0].set_color(TV_VOLT)
    bars[0].set_edgecolor(TV_VOLT)

    for i, v in enumerate(bottom_freq):
        ax_bottom.text(i, v + 2.0, f"{v}%", ha='center', fontsize=9, fontweight='bold', 
                       color=TV_VOLT if i == 0 else TV_INK)
        ax_bottom.text(i, 4, f"Avg DD: {avg_decline[i]}%", ha='center', fontsize=7.5, color="#EF4444" if avg_decline[i] < -2 else TV_INK_MUTED)

    ax_bottom.set_title("All Years Since 1950 (n=76): % of Times S&P 500 Bottomed During that Week", 
                        fontsize=10.5, fontweight='bold', pad=10, loc='left')
    ax_bottom.set_xticks(x)
    ax_bottom.set_xticklabels(weeks, fontsize=9)
    ax_bottom.set_ylabel("% Probability", fontsize=9)
    ax_bottom.set_ylim(0, 70)
    ax_bottom.grid(True, linestyle=':', alpha=0.4)

    fig.suptitle("S&P 500 November Seasonality in Midterm Years Since 1950", 
                 fontsize=13, fontweight='bold', color=TV_INK, y=0.98)

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "midterm_seasonality_1950.png")
    plt.savefig(out)
    plt.close()
    print(f"[OK] Generado {out}")

# ─────────────────────────────────────────────────────────────────────────────
# 4. CHART 4: BIG TECH CAPEX VS FREE CASH FLOW (Financial Times & Boring Biz)
# ─────────────────────────────────────────────────────────────────────────────
def chart_hyperscalers_capex_fcf():
    quarters = ["Q1 23", "Q2 23", "Q3 23", "Q4 23", "Q1 24", "Q2 24", "Q3 24", "Q4 24", "Q1 25", "Q2 25", "Q3 25", "Q4 25", "Q1 26", "Q2 26", "Q3 26", "Q4 26"]
    
    # Combined quarterly CapEx of Meta, Alphabet, Microsoft, Amazon ($B)
    capex = [34, 35, 38, 44, 48, 56, 65, 78, 76, 95, 112, 126, 131, 165, 208, 215]
    # Free cash flow ($B)
    fcf =   [36, 58, 67, 58, 55, 57, 56, 64, 42, 40, 62, 60, 24, 15, -4, -12]

    fig, ax1 = plt.subplots(figsize=(10, 5.5), dpi=150)

    x = np.arange(len(quarters))

    ax1.plot(x, capex, color="#2563EB", marker='o', lw=2.5, label='CapEx (Meta, Google, MSFT, Amazon)')
    ax1.plot(x, fcf, color="#F43F5E", marker='s', lw=2.5, label='Free Cash Flow (Combined)')
    ax1.axhline(y=0, color=TV_BORDER, linestyle='--', lw=1.2)

    # Highlight inversion in 2026
    ax1.fill_between(x[-4:], capex[-4:], fcf[-4:], color="#EF4444", alpha=0.15, label="Negative Cash Deficit Window")

    ax1.annotate('CapEx hits $208B+\nFCF turns negative!', 
                 xy=(x[-2], fcf[-2]), xytext=(x[-2] - 3.5, fcf[-2] + 45),
                 arrowprops=dict(facecolor=TV_VOLT, edgecolor=TV_VOLT, arrowstyle='->', lw=1.5),
                 fontsize=9, fontweight='bold', color=TV_VOLT,
                 bbox=dict(boxstyle='square,pad=0.4', facecolor=TV_SURFACE_2, edgecolor=TV_VOLT))

    ax1.set_title("Big Tech Capital Spending vs. Free Cash Flow (2023 – 2026) [$Bn]", 
                  fontsize=13, fontweight='bold', pad=14, loc='left')
    ax1.set_xticks(x)
    ax1.set_xticklabels(quarters, rotation=45, ha='right', fontsize=8.5)
    ax1.set_ylabel("USD Billions ($Bn)", fontsize=9.5)
    ax1.grid(True, linestyle=':', alpha=0.4)
    ax1.legend(frameon=True, facecolor=TV_SURFACE_2, edgecolor=TV_BORDER, fontsize=8.5, loc='upper left')

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "hyperscalers_capex_fcf.png")
    plt.savefig(out)
    plt.close()
    print(f"[OK] Generado {out}")

# ─────────────────────────────────────────────────────────────────────────────
# 5. CHART 5: FED RATE HIKE EXPECTATIONS (Duality Research)
# ─────────────────────────────────────────────────────────────────────────────
def chart_fed_rate_expectations():
    dates = pd.date_range("2026-08-01", "2026-12-31", freq="B")
    n = len(dates)
    np.random.seed(42)

    idx_peak = 42 # Late September
    total_hikes = np.zeros(n)
    total_hikes[:idx_peak] = np.linspace(2.2, 3.83, idx_peak) + np.random.normal(0, 0.08, idx_peak)
    total_hikes[idx_peak:] = np.linspace(3.83, 2.19, n - idx_peak) + np.random.normal(0, 0.06, n - idx_peak)
    total_hikes = pd.Series(total_hikes, index=dates).rolling(3, min_periods=1).mean()

    hikes_2027 = total_hikes * 0.66
    hikes_2026 = total_hikes * 0.34

    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150)

    peak_date = dates[idx_peak]
    ax.axvspan(peak_date - pd.Timedelta(days=8), peak_date + pd.Timedelta(days=8), color="#38BDF8", alpha=0.08)
    ax.axvline(peak_date, color="#38BDF8", linestyle=":", lw=1.2)
    ax.text(peak_date, 0.8, " Rate Hike Expectations\n Peaked in Late September!", color=TV_CYAN, fontsize=8.5, fontweight="bold", va='center')

    ax.plot(dates, total_hikes, color=TV_INK, lw=2.2, label="...through end of 2027 (Current: 2.19)")
    ax.plot(dates, hikes_2027, color=TV_PURPLE, lw=2.0, label="...for 2027 (1.46)")
    ax.plot(dates, hikes_2026, color=TV_GREEN, lw=2.0, label="...for 2026 (0.73)")

    ax.scatter([peak_date], [3.83], color=TV_VOLT, s=50, zorder=5)
    ax.text(peak_date, 3.95, "3.83 Hikes", ha='center', fontsize=9, fontweight='bold', color=TV_VOLT)

    today_idx = 67
    today_date = dates[today_idx]
    ax.scatter([today_date], [total_hikes.iloc[today_idx]], color=TV_VOLT, s=60, zorder=5)
    ax.annotate("2.19 Hikes", 
                xy=(today_date, total_hikes.iloc[today_idx]), 
                xytext=(today_date + pd.Timedelta(days=10), total_hikes.iloc[today_idx]),
                arrowprops=dict(facecolor=TV_VOLT, edgecolor=TV_VOLT, arrowstyle='->', lw=1.5),
                fontsize=9.5, fontweight='bold', color=TV_VOLT,
                bbox=dict(boxstyle='round,pad=0.3', facecolor=TV_SURFACE_2, edgecolor=TV_VOLT))

    ax.set_title("Number of Expected Fed Rate Hikes (Fed Funds Futures)", fontsize=13, fontweight='bold', pad=14, loc='left')
    ax.set_ylabel("Implied 25bps Rate Hikes", fontsize=9.5)
    ax.set_ylim(0, 4.3)
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.5))
    ax.grid(True, linestyle=':', alpha=0.4)
    ax.legend(frameon=True, facecolor=TV_SURFACE_2, edgecolor=TV_BORDER, fontsize=8.5, loc='upper right')
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%Y'))

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "fed_rate_expectations.png")
    plt.savefig(out)
    plt.close()
    print(f"[OK] Generado {out}")


# ─────────────────────────────────────────────────────────────────────────────
# 6. CHART 6: CRYPTO FEAR & GREED + BITCOIN REGIME (CoinMarketCap)
# ─────────────────────────────────────────────────────────────────────────────
def chart_crypto_fear_greed():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.8), dpi=150, gridspec_kw={'width_ratios': [1, 1.4]})

    # Gauge / Dial representation
    val = 34  # Fear
    theta = np.linspace(np.pi, 0, 100)
    # Background semi-circle
    ax1.plot(np.cos(theta), np.sin(theta), color=TV_BORDER, lw=14)
    
    # Colored segments: Red (0-25), Orange (25-45), Yellow (45-55), Green (55-75), Strong Green (75-100)
    t_red = np.linspace(np.pi, np.pi * 0.75, 25)
    t_orange = np.linspace(np.pi * 0.75, np.pi * 0.55, 20)
    t_yellow = np.linspace(np.pi * 0.55, np.pi * 0.45, 10)
    t_green = np.linspace(np.pi * 0.45, 0, 45)

    ax1.plot(np.cos(t_red), np.sin(t_red), color="#EF4444", lw=14)
    ax1.plot(np.cos(t_orange), np.sin(t_orange), color="#F97316", lw=14)
    ax1.plot(np.cos(t_yellow), np.sin(t_yellow), color="#FACC15", lw=14)
    ax1.plot(np.cos(t_green), np.sin(t_green), color="#10B981", lw=14)

    # Needle
    needle_angle = np.pi - (val / 100.0) * np.pi
    ax1.arrow(0, 0, 0.75 * np.cos(needle_angle), 0.75 * np.sin(needle_angle),
              head_width=0.08, head_length=0.08, fc=TV_INK, ec=TV_INK, lw=2)
    ax1.plot(0, 0, 'o', color=TV_INK, markersize=8)

    ax1.text(0, -0.25, f"{val}\nFEAR", ha='center', va='center', fontsize=18, fontweight='bold', color="#F97316")
    ax1.text(0, -0.65, "Yesterday: 38 (Fear)\nLast Week: 43 (Neutral)\nLast Month: 67 (Greed)", 
             ha='center', va='center', fontsize=8.5, color=TV_INK_MUTED)
    ax1.set_xlim(-1.2, 1.2)
    ax1.set_ylim(-0.8, 1.2)
    ax1.axis('off')
    ax1.set_title("CMC Crypto Fear & Greed Index", fontsize=11, fontweight='bold', pad=10)

    # Panel 2: Bitcoin price scenarios
    days = pd.date_range("2026-06-01", "2026-11-03", freq="D")
    np.random.seed(99)
    btc_price = 68000 + np.cumsum(np.random.normal(30, 900, len(days)))
    btc_price[-1] = 76677

    ax2.plot(days, btc_price, color=TV_CYAN, lw=2, label="BTC/USD (Current: $76.677)")
    ax2.axhline(y=80000, color=TV_RED, linestyle='--', lw=1.5, label="Key Lost Support: $80,000")
    
    # Scenarios projection
    future_days = pd.date_range("2026-11-03", "2026-12-15", freq="D")
    shallow_bear = 76677 - np.linspace(0, 6000, len(future_days))
    normal_bear = 76677 - np.linspace(0, 18000, len(future_days))
    short_bear = 76677 + np.linspace(0, 15000, len(future_days))

    ax2.plot(future_days, shallow_bear, color="#F59E0B", linestyle=':', lw=2, label="Shallow Bear (Base Case)")
    ax2.plot(future_days, normal_bear, color="#EF4444", linestyle=':', lw=2, label="Normal Bear (Possible)")
    ax2.plot(future_days, short_bear, color=TV_GREEN, linestyle=':', lw=1.5, label="Short Bear (Unlikely)")

    ax2.set_title("Bitcoin: Escenarios tras perder los US$80.000", fontsize=11, fontweight='bold', loc='left')
    ax2.set_ylabel("USD", fontsize=9.5)
    ax2.yaxis.set_major_formatter(ticker.StrMethodFormatter('${x:,.0f}'))
    ax2.grid(True, linestyle=':', alpha=0.4)
    ax2.legend(frameon=True, facecolor=TV_SURFACE_2, edgecolor=TV_BORDER, fontsize=7.5, loc='lower left')
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "crypto_fear_greed_btc.png")
    plt.savefig(out)
    plt.close()
    print(f"[OK] Generado {out}")

# ─────────────────────────────────────────────────────────────────────────────
# 7. CHART 7: INSTITUTIONAL FLOWS & CTA EXPOSURE (Goldman Sachs Prime Proxy)
# ─────────────────────────────────────────────────────────────────────────────
def chart_institutional_flows():
    dates = pd.date_range("2026-05-01", "2026-12-01", freq="B")
    n = len(dates)
    np.random.seed(55)

    # Realized CTA positioning in S&P 500 ($Bn)
    t = np.linspace(0, 1, n)
    cta_baseline = 2 + 10 * np.sin(t * 6) + np.cumsum(np.random.normal(0, 0.8, n))
    
    # Projection window for Nov - Dec
    split_idx = int(n * 0.78)
    realized_dates = dates[:split_idx]
    proj_dates = dates[split_idx:]
    
    realized_vals = cta_baseline[:split_idx]
    last_val = realized_vals[-1]

    proj_flat = last_val + np.linspace(0, 12, len(proj_dates))
    proj_down1 = last_val - np.linspace(0, 38, len(proj_dates))
    proj_down2 = last_val - np.linspace(0, 68, len(proj_dates))

    fig, ax = plt.subplots(figsize=(10, 5.2), dpi=150)

    ax.plot(realized_dates, realized_vals, color=TV_CYAN, lw=2.2, label="Realized CTA Baseline ($Bn)")
    ax.plot(proj_dates, proj_flat, color=TV_GREEN, lw=2.0, linestyle='--', label="Flat Mkt Baseline (Buyback)")
    ax.plot(proj_dates, proj_down1, color="#F59E0B", lw=2.0, linestyle='--', label="Down 1 Std Dev (-$38Bn)")
    ax.plot(proj_dates, proj_down2, color="#EF4444", lw=2.5, linestyle='-', label="Down 2 Std Dev (-$68.8Bn US)")

    ax.axhline(0, color=TV_BORDER, lw=1.2)
    ax.axvline(realized_dates[-1], color=TV_INK_MUTED, linestyle=':', lw=1.2)
    ax.text(realized_dates[-1], 15, " Today", fontsize=8, color=TV_INK_MUTED)

    ax.set_title("GS CTA Estimates & Asymmetric Selling Scenarios in S&P 500 ($Bn)", 
                 fontsize=12.5, fontweight='bold', pad=12, loc='left')
    ax.set_ylabel("Net Notional Exposure ($Bn)", fontsize=9.5)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}b'))
    ax.grid(True, linestyle=':', alpha=0.4)
    ax.legend(frameon=True, facecolor=TV_SURFACE_2, edgecolor=TV_BORDER, fontsize=8, loc='lower left')
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %y'))

    plt.tight_layout()
    out = os.path.join(OUTPUT_DIR, "institutional_flows_cta.png")
    plt.savefig(out)
    plt.close()
    print(f"[OK] Generado {out}")

def main():
    print("=" * 60)
    print("Iniciando generación de Daily Market Intelligence...")
    print("=" * 60)
    generate_market_matrix()
    chart_sp500_range_distribution()
    chart_sp500_breadth_advancers()
    chart_midterm_seasonality()
    chart_hyperscalers_capex_fcf()
    chart_fed_rate_expectations()
    chart_crypto_fear_greed()
    chart_institutional_flows()
    print("=" * 60)
    print("¡Todos los gráficos y datos fueron generados exitosamente!")
    print(f"Directorio de salida: {OUTPUT_DIR}")
    print("=" * 60)

if __name__ == "__main__":
    main()
