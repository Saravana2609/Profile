//+------------------------------------------------------------------+
//|                                                     CandleEA.mq5  |
//|                                                                  |
//|  Candle-momentum Expert Advisor.                                 |
//|                                                                  |
//|  Core idea (unchanged from the original): trade in the direction |
//|  of the last completed candle. A bullish close -> buy, a bearish |
//|  close -> sell, with the previous candle's extreme as the stop   |
//|  and a fixed reward:risk take-profit.                            |
//|                                                                  |
//|  Improvements over the original:                                 |
//|   * Robust new-bar detection (acts once per bar, always).        |
//|   * Magic number so the EA only manages its own positions.       |
//|   * One open position at a time (no stacking every candle).      |
//|   * Risk-based position sizing (% of balance) with safe fallback.|
//|   * Trend filter (EMA), body-size filter, spread filter and an   |
//|     optional trading-session window to skip low-quality setups.  |
//|   * Broker-aware price handling: digits/tick normalization and   |
//|     stops-level enforcement so SL/TP are never rejected.         |
//|   * Optional break-even and trailing-stop management.            |
//+------------------------------------------------------------------+
#property copyright "Saravana Raj"
#property version   "2.00"
#property strict

#include <Trade/Trade.mqh>

//--- Inputs ---------------------------------------------------------
input group "General"
input ulong  InpMagic        = 990026;   // Magic number
input double InpRRR          = 2.0;       // Reward : Risk ratio
input int    InpSlippage     = 20;        // Max deviation (points)
input bool   InpDebug        = true;      // Print diagnostics to the Experts log

input group "Position sizing"
input bool   InpUseRiskSizing = true;     // Size lot by risk % of balance
input double InpRiskPercent   = 1.0;      // Risk per trade (% of balance)
input double InpFixedLot      = 0.10;     // Fixed lot (used if risk sizing off / fails)

input group "Entry filters"
input bool   InpUseTrendFilter = true;    // Only trade with the EMA trend
input int    InpEmaPeriod      = 50;      // Trend EMA period
input double InpMinBodyPoints  = 50;      // Min candle body size (points), 0 = off
input double InpMaxSpreadPoints= 0;       // Max allowed spread (points), 0 = off

input group "Session (server time)"
input bool   InpUseSession   = false;     // Restrict trading to a time window
input int    InpStartHour    = 7;         // Session start hour (0-23)
input int    InpEndHour      = 20;        // Session end hour (0-23)

input group "Trade management"
input bool   InpUseBreakEven = true;      // Move SL to break-even
input double InpBreakEvenRR  = 1.0;       // Trigger BE at this R multiple
input bool   InpUseTrailing  = false;     // Trailing stop
input double InpTrailPoints  = 200;       // Trailing distance (points)

//--- Globals --------------------------------------------------------
CTrade        trade;
datetime      last_bar_time = 0;
int           ema_handle    = INVALID_HANDLE;
double        g_point;
int           g_digits;
double        g_stops_level;   // min distance (price) for SL/TP from market

//+------------------------------------------------------------------+
int OnInit()
{
   g_point  = SymbolInfoDouble(_Symbol, SYMBOL_POINT);
   g_digits = (int)SymbolInfoInteger(_Symbol, SYMBOL_DIGITS);
   g_stops_level = (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL) * g_point;

   trade.SetExpertMagicNumber(InpMagic);
   trade.SetDeviationInPoints(InpSlippage);
   trade.SetTypeFillingBySymbol(_Symbol);

   if(InpUseTrendFilter)
   {
      ema_handle = iMA(_Symbol, _Period, InpEmaPeriod, 0, MODE_EMA, PRICE_CLOSE);
      if(ema_handle == INVALID_HANDLE)
      {
         Print("Failed to create EMA handle");
         return(INIT_FAILED);
      }
   }

   if(InpRRR <= 0.0)
   {
      Print("RRR must be greater than 0");
      return(INIT_PARAMETERS_INCORRECT);
   }

   last_bar_time = iTime(_Symbol, _Period, 0);

   if(InpDebug)
   {
      double spread = (SymbolInfoDouble(_Symbol, SYMBOL_ASK) -
                       SymbolInfoDouble(_Symbol, SYMBOL_BID)) / g_point;
      PrintFormat("[CandleEA] %s digits=%d point=%.5f stops_level=%.1f pts | "
                  "spread now=%.1f pts | lot min/step/max=%.2f/%.2f/%.2f | "
                  "tickSize=%.5f tickValue=%.5f",
                  _Symbol, g_digits, g_point,
                  (double)SymbolInfoInteger(_Symbol, SYMBOL_TRADE_STOPS_LEVEL),
                  spread,
                  SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN),
                  SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP),
                  SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX),
                  SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE),
                  SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE));
   }
   return(INIT_SUCCEEDED);
}
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
{
   if(ema_handle != INVALID_HANDLE)
      IndicatorRelease(ema_handle);
}
//+------------------------------------------------------------------+
void OnTick()
{
   // Manage any open position on every tick (BE / trailing).
   ManageOpenPosition();

   // Strategy logic runs once per fully-formed bar.
   if(!IsNewBar())
      return;

   // Skip if we already hold a position from this EA.
   if(HasOpenPosition())
      return;

   if(!SessionAllowed())
      { Skip("session"); return; }

   if(!SpreadAllowed())
      { Skip("spread"); return; }

   // Previous (just-closed) candle.
   double open  = iOpen(_Symbol, _Period, 1);
   double close = iClose(_Symbol, _Period, 1);
   double high  = iHigh(_Symbol, _Period, 1);
   double low   = iLow(_Symbol, _Period, 1);

   double body = MathAbs(close - open);
   if(InpMinBodyPoints > 0 && body < InpMinBodyPoints * g_point)
      { Skip("body<min"); return; }  // candle too small, no edge

   double ask = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double bid = SymbolInfoDouble(_Symbol, SYMBOL_BID);

   bool bullish = (close > open);
   bool bearish = (close < open);

   if(!bullish && !bearish)
      { Skip("doji"); return; }

   // Trend filter: only trade in the EMA direction.
   if(InpUseTrendFilter)
   {
      double ema = TrendEma();
      if(ema == 0.0)
         { Skip("ema-unavailable"); return; }
      if(bullish && close < ema) { Skip("buy-vs-trend"); return; }
      if(bearish && close > ema) { Skip("sell-vs-trend"); return; }
   }

   if(bullish)
      OpenTrade(ORDER_TYPE_BUY, ask, low);
   else if(bearish)
      OpenTrade(ORDER_TYPE_SELL, bid, high);
}
//+------------------------------------------------------------------+
//| Open a trade with normalized, stops-level-safe SL/TP.            |
//+------------------------------------------------------------------+
void OpenTrade(const ENUM_ORDER_TYPE type, double entry, double rawStop)
{
   entry = NormalizePrice(entry);
   double sl, tp;

   if(type == ORDER_TYPE_BUY)
   {
      sl = NormalizePrice(rawStop);
      // Enforce minimum stop distance below entry.
      if(entry - sl < g_stops_level)
         sl = NormalizePrice(entry - g_stops_level);

      double risk = entry - sl;
      if(risk <= 0) return;
      tp = NormalizePrice(entry + risk * InpRRR);
      if(tp - entry < g_stops_level)
         tp = NormalizePrice(entry + g_stops_level);
   }
   else // SELL
   {
      sl = NormalizePrice(rawStop);
      if(sl - entry < g_stops_level)
         sl = NormalizePrice(entry + g_stops_level);

      double risk = sl - entry;
      if(risk <= 0) return;
      tp = NormalizePrice(entry - risk * InpRRR);
      if(entry - tp < g_stops_level)
         tp = NormalizePrice(entry - g_stops_level);
   }

   double slDistance = MathAbs(entry - sl);
   double lot = CalcLot(slDistance);
   if(lot <= 0)
      return;

   bool ok;
   if(type == ORDER_TYPE_BUY)
      ok = trade.Buy(lot, _Symbol, entry, sl, tp);
   else
      ok = trade.Sell(lot, _Symbol, entry, sl, tp);

   if(!ok)
      PrintFormat("[CandleEA] Order FAILED: %s lot=%.2f entry=%.*f sl=%.*f tp=%.*f "
                  "retcode=%d (%s)",
                  (type == ORDER_TYPE_BUY ? "BUY" : "SELL"), lot,
                  g_digits, entry, g_digits, sl, g_digits, tp,
                  trade.ResultRetcode(), trade.ResultRetcodeDescription());
   else if(InpDebug)
      PrintFormat("[CandleEA] Order OK: %s lot=%.2f entry=%.*f sl=%.*f tp=%.*f",
                  (type == ORDER_TYPE_BUY ? "BUY" : "SELL"), lot,
                  g_digits, entry, g_digits, sl, g_digits, tp);
}
//+------------------------------------------------------------------+
//| Manage the open position: break-even and trailing stop.          |
//+------------------------------------------------------------------+
void ManageOpenPosition()
{
   if(!HasOpenPosition())
      return;
   if(!InpUseBreakEven && !InpUseTrailing)
      return;

   long   type     = PositionGetInteger(POSITION_TYPE);
   double openP    = PositionGetDouble(POSITION_PRICE_OPEN);
   double curSL    = PositionGetDouble(POSITION_SL);
   double curTP    = PositionGetDouble(POSITION_TP);
   double bid      = SymbolInfoDouble(_Symbol, SYMBOL_BID);
   double ask      = SymbolInfoDouble(_Symbol, SYMBOL_ASK);
   double newSL    = curSL;

   if(type == POSITION_TYPE_BUY)
   {
      double initRisk = openP - PositionGetDouble(POSITION_SL);
      // Break-even
      if(InpUseBreakEven && initRisk > 0 &&
         bid - openP >= initRisk * InpBreakEvenRR && curSL < openP)
         newSL = NormalizePrice(openP);
      // Trailing
      if(InpUseTrailing)
      {
         double trail = NormalizePrice(bid - InpTrailPoints * g_point);
         if(trail > newSL) newSL = trail;
      }
      if(newSL > curSL && bid - newSL >= g_stops_level)
         trade.PositionModify(_Symbol, newSL, curTP);
   }
   else if(type == POSITION_TYPE_SELL)
   {
      double initRisk = PositionGetDouble(POSITION_SL) - openP;
      if(InpUseBreakEven && initRisk > 0 &&
         openP - ask >= initRisk * InpBreakEvenRR && (curSL > openP || curSL == 0))
         newSL = NormalizePrice(openP);
      if(InpUseTrailing)
      {
         double trail = NormalizePrice(ask + InpTrailPoints * g_point);
         if(newSL == 0 || trail < newSL) newSL = trail;
      }
      if(newSL != curSL && newSL > 0 && newSL - ask >= g_stops_level &&
         (newSL < curSL || curSL == 0))
         trade.PositionModify(_Symbol, newSL, curTP);
   }
}
//+------------------------------------------------------------------+
//| Helpers                                                          |
//+------------------------------------------------------------------+
void Skip(const string reason)
{
   if(InpDebug)
      PrintFormat("[CandleEA] %s skip: %s",
                  TimeToString(iTime(_Symbol, _Period, 0), TIME_DATE | TIME_MINUTES),
                  reason);
}

bool IsNewBar()
{
   datetime t = iTime(_Symbol, _Period, 0);
   if(t != last_bar_time)
   {
      last_bar_time = t;
      return true;
   }
   return false;
}

bool HasOpenPosition()
{
   if(!PositionSelect(_Symbol))
      return false;
   return (PositionGetInteger(POSITION_MAGIC) == (long)InpMagic);
}

bool SessionAllowed()
{
   if(!InpUseSession)
      return true;
   MqlDateTime dt;
   TimeToStruct(TimeCurrent(), dt);
   int h = dt.hour;
   if(InpStartHour <= InpEndHour)
      return (h >= InpStartHour && h < InpEndHour);
   // Overnight window (e.g. 22 -> 6)
   return (h >= InpStartHour || h < InpEndHour);
}

bool SpreadAllowed()
{
   if(InpMaxSpreadPoints <= 0)
      return true;
   double spread = (SymbolInfoDouble(_Symbol, SYMBOL_ASK) -
                    SymbolInfoDouble(_Symbol, SYMBOL_BID)) / g_point;
   return (spread <= InpMaxSpreadPoints);
}

double TrendEma()
{
   if(ema_handle == INVALID_HANDLE)
      return 0.0;
   double buf[];
   if(CopyBuffer(ema_handle, 0, 1, 1, buf) <= 0)
      return 0.0;
   return buf[0];
}

double NormalizePrice(double price)
{
   double tick = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);
   if(tick > 0)
      price = MathRound(price / tick) * tick;
   return NormalizeDouble(price, g_digits);
}

double NormalizeLot(double lot)
{
   double minLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_MAX);
   double step   = SymbolInfoDouble(_Symbol, SYMBOL_VOLUME_STEP);
   if(step > 0)
      lot = MathFloor(lot / step) * step;
   lot = MathMax(minLot, MathMin(maxLot, lot));
   return lot;
}

double CalcLot(double slDistancePrice)
{
   if(!InpUseRiskSizing || slDistancePrice <= 0)
      return NormalizeLot(InpFixedLot);

   double balance   = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskMoney = balance * InpRiskPercent / 100.0;
   double tickValue = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_VALUE);
   double tickSize  = SymbolInfoDouble(_Symbol, SYMBOL_TRADE_TICK_SIZE);

   if(tickValue <= 0 || tickSize <= 0)
      return NormalizeLot(InpFixedLot);

   double lossPerLot = (slDistancePrice / tickSize) * tickValue;
   if(lossPerLot <= 0)
      return NormalizeLot(InpFixedLot);

   double lot = riskMoney / lossPerLot;
   return NormalizeLot(lot);
}
//+------------------------------------------------------------------+
