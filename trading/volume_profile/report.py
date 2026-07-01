"""Reporting and visuals: Volume Profile chart, equity curve, timeframe
comparison, and daily/weekly performance — assembled into one self-contained
HTML report.

Uses matplotlib's non-interactive Agg backend so it runs headless (cloud, cron,
no display). Images are embedded as base64 so the report is a single portable
file.
"""

from __future__ import annotations

import base64
import io

import matplotlib

matplotlib.use("Agg")  # headless
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .backtest import Trade
from .profile import VolumeProfile


def _fig_to_base64(fig) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


def plot_volume_profile(bars: pd.DataFrame, vp: VolumeProfile, title: str) -> str:
    """Price over the window (left) beside its volume-by-price histogram (right)."""
    fig, (axp, axv) = plt.subplots(
        1, 2, figsize=(11, 5), sharey=True, gridspec_kw={"width_ratios": [3, 1]}
    )
    axp.plot(bars["time"], bars["close"], color="#1f77b4", lw=0.8)
    for lvl, name, color in [
        (vp.poc, "POC", "#d62728"),
        (vp.vah, "VAH", "#2ca02c"),
        (vp.val, "VAL", "#2ca02c"),
    ]:
        axp.axhline(lvl, color=color, ls="--", lw=1)
        axp.text(bars["time"].iloc[0], lvl, f" {name} {lvl:.2f}", va="bottom",
                 color=color, fontsize=8)
    axp.axhspan(vp.val, vp.vah, color="#2ca02c", alpha=0.06)
    axp.set_title(title)
    axp.set_ylabel("Price")
    axp.grid(alpha=0.2)

    axv.barh(vp.bin_prices, vp.bin_volumes, height=(vp.bin_prices[1] - vp.bin_prices[0]),
             color="#8888cc", alpha=0.8)
    axv.axhline(vp.poc, color="#d62728", ls="--", lw=1)
    axv.set_title("Volume by price")
    axv.grid(alpha=0.2)
    return _fig_to_base64(fig)


def plot_equity(trades: list[Trade], title: str) -> str:
    """Cumulative R equity curve with drawdown shading."""
    fig, ax = plt.subplots(figsize=(11, 4))
    if trades:
        times = [t.exit_time for t in trades]
        r = np.array([t.r_multiple for t in trades])
        eq = np.cumsum(r)
        peak = np.maximum.accumulate(eq)
        ax.plot(times, eq, color="#1f77b4", lw=1.3, label="Equity (R)")
        ax.fill_between(times, eq, peak, color="#d62728", alpha=0.15, label="Drawdown")
        ax.axhline(0, color="grey", lw=0.8)
        ax.legend(loc="upper left", fontsize=8)
    else:
        ax.text(0.5, 0.5, "No trades", ha="center", va="center")
    ax.set_title(title)
    ax.set_ylabel("Cumulative R")
    ax.grid(alpha=0.2)
    return _fig_to_base64(fig)


def plot_timeframe_comparison(results: list[dict]) -> str:
    """Bar charts of expectancy and win rate per timeframe."""
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
    tfs = [r["timeframe"] for r in results]
    exp = [r["metrics"].get("expectancy_R", 0) for r in results]
    wr = [r["metrics"].get("win_rate", 0) * 100 for r in results]

    colors = ["#2ca02c" if e > 0 else "#d62728" for e in exp]
    a1.bar(tfs, exp, color=colors)
    a1.axhline(0, color="grey", lw=0.8)
    a1.set_title("Expectancy (R per trade)")
    a1.grid(alpha=0.2, axis="y")

    a2.bar(tfs, wr, color="#1f77b4")
    a2.axhline(50, color="grey", ls="--", lw=0.8)
    a2.set_title("Win rate (%)")
    a2.grid(alpha=0.2, axis="y")
    return _fig_to_base64(fig)


def _period_frame(trades: list[Trade]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time": [t.entry_time for t in trades],
            "r": [t.r_multiple for t in trades],
        }
    )


def daily_table(trades: list[Trade]) -> pd.DataFrame:
    if not trades:
        return pd.DataFrame()
    df = _period_frame(trades)
    df["day"] = df["time"].dt.date
    g = df.groupby("day")["r"].agg(
        trades="count", win_rate=lambda s: (s > 0).mean(), total_R="sum"
    )
    return g.reset_index()


def weekly_table(trades: list[Trade]) -> pd.DataFrame:
    if not trades:
        return pd.DataFrame()
    df = _period_frame(trades)
    iso = df["time"].dt.isocalendar()
    df["week"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
    g = df.groupby("week")["r"].agg(
        trades="count", win_rate=lambda s: (s > 0).mean(), total_R="sum"
    )
    return g.reset_index()


def plot_period_pnl(trades: list[Trade]) -> str:
    """Daily and weekly R bars."""
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6))
    d = daily_table(trades)
    w = weekly_table(trades)
    if len(d):
        a1.bar(range(len(d)), d["total_R"],
               color=["#2ca02c" if x > 0 else "#d62728" for x in d["total_R"]])
        a1.set_xticks(range(len(d)))
        a1.set_xticklabels([str(x) for x in d["day"]], rotation=90, fontsize=6)
    a1.axhline(0, color="grey", lw=0.8)
    a1.set_title("Daily P&L (R)")
    a1.grid(alpha=0.2, axis="y")
    if len(w):
        a2.bar(range(len(w)), w["total_R"],
               color=["#2ca02c" if x > 0 else "#d62728" for x in w["total_R"]])
        a2.set_xticks(range(len(w)))
        a2.set_xticklabels(w["week"], rotation=90, fontsize=6)
    a2.axhline(0, color="grey", lw=0.8)
    a2.set_title("Weekly P&L (R)")
    a2.grid(alpha=0.2, axis="y")
    fig.tight_layout()
    return _fig_to_base64(fig)


def _df_to_html(df: pd.DataFrame) -> str:
    if df.empty:
        return "<p><em>No trades.</em></p>"
    df = df.copy()
    if "win_rate" in df:
        df["win_rate"] = (df["win_rate"] * 100).round(1).astype(str) + "%"
    if "total_R" in df:
        df["total_R"] = df["total_R"].round(2)
    return df.to_html(index=False, border=0, classes="tbl")


def _metrics_to_html(m: dict) -> str:
    rows = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in m.items())
    return f"<table class='tbl'>{rows}</table>"


def build_html_report(
    *,
    symbol: str,
    results: list[dict],
    best: dict,
    vp_img: str,
    equity_img: str,
    tf_img: str,
    period_img: str,
    daily: pd.DataFrame,
    weekly: pd.DataFrame,
    generated: str,
    is_synthetic: bool,
) -> str:
    warn = (
        "<div class='warn'>⚠️ Data is <b>synthetic</b> — numbers only prove the "
        "pipeline works. Run on real MT5 data for a real verdict.</div>"
        if is_synthetic
        else "<div class='ok'>Data source: real export.</div>"
    )
    tf_rows = "".join(
        f"<tr><td>{r['timeframe']}</td>"
        f"<td>{r['metrics'].get('trades', 0)}</td>"
        f"<td>{r['metrics'].get('win_rate', 0) * 100:.1f}%</td>"
        f"<td>{r['metrics'].get('expectancy_R', 0):+.3f}</td>"
        f"<td>{r['metrics'].get('profit_factor', 0)}</td>"
        f"<td>{r['metrics'].get('total_R', 0):+.1f}</td></tr>"
        for r in results
    )
    return f"""<!doctype html><html><head><meta charset='utf-8'>
<title>{symbol} Volume Profile Report</title>
<style>
 body{{font-family:-apple-system,Segoe UI,Arial,sans-serif;margin:24px;color:#222;background:#fafafa}}
 h1{{margin-bottom:0}} h2{{border-bottom:2px solid #eee;padding-bottom:4px;margin-top:32px}}
 .sub{{color:#888}} img{{max-width:100%;border:1px solid #eee;border-radius:6px;background:#fff}}
 .tbl{{border-collapse:collapse;margin:8px 0}} .tbl td,.tbl th{{padding:5px 12px;border-bottom:1px solid #eee;text-align:right}}
 .tbl td:first-child,.tbl th:first-child{{text-align:left}}
 .warn{{background:#fff3cd;border:1px solid #ffe08a;padding:10px;border-radius:6px;margin:12px 0}}
 .ok{{background:#e7f5e7;border:1px solid #b6e0b6;padding:10px;border-radius:6px;margin:12px 0}}
 .best{{background:#e7f0ff;border:1px solid #b6d0f0;padding:12px;border-radius:6px;font-size:18px}}
 .cols{{display:flex;gap:24px;flex-wrap:wrap}}
</style></head><body>
<h1>{symbol} — Volume Profile Strategy Report</h1>
<div class='sub'>Generated {generated}</div>
{warn}

<h2>1. Best timeframe</h2>
<div class='best'>🏆 <b>{best['timeframe']}</b> — expectancy
 <b>{best['metrics'].get('expectancy_R', 0):+.3f} R/trade</b>,
 win rate {best['metrics'].get('win_rate', 0) * 100:.1f}%,
 profit factor {best['metrics'].get('profit_factor', 0)}
 over {best['metrics'].get('trades', 0)} trades.</div>
<p>Ranked by expectancy (with a minimum trade count). Win rate alone does not
decide the winner — expectancy and profit factor do.</p>
<table class='tbl'>
<tr><th>Timeframe</th><th>Trades</th><th>Win rate</th><th>Expectancy R</th><th>Profit factor</th><th>Total R</th></tr>
{tf_rows}
</table>
<img src='data:image/png;base64,{tf_img}'/>

<h2>2. Volume Profile (latest window, {best['timeframe']})</h2>
<img src='data:image/png;base64,{vp_img}'/>

<h2>3. Equity curve ({best['timeframe']})</h2>
<img src='data:image/png;base64,{equity_img}'/>
<div class='cols'><div><b>Full-sample metrics</b>{_metrics_to_html(best['metrics'])}</div></div>

<h2>4. Daily &amp; weekly performance ({best['timeframe']})</h2>
<img src='data:image/png;base64,{period_img}'/>
<div class='cols'>
 <div><b>Weekly</b>{_df_to_html(weekly)}</div>
 <div><b>Daily (last 15)</b>{_df_to_html(daily.tail(15))}</div>
</div>

<p class='sub'>Research/education only. Not financial advice. Trading XAUUSD
carries substantial risk.</p>
</body></html>"""
