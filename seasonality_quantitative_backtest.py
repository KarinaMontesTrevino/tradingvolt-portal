import os
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime

# ==============================================================================
# RIGOROUS SEASONALITY QUANTITATIVE AUDIT & BACKTEST ENGINE
# Evaluates:
# 1. "Sell in May" / Halloween Indicator (Nov-Apr vs May-Oct)
# 2. Turn-of-the-Month (TOTM) Effect (Last day + first 4 days)
# 3. Monthly Heatmap & Monthly Win-Rate Breakdown
# 4. Top Seasonal Months Strategy vs Buy & Hold
# 5. Commodity Specific Seasonalities (Crude Oil, Gold, Natural Gas, Corn)
# ==============================================================================

def compute_metrics(equity_series: pd.Series, risk_free: float = 0.02):
    if equity_series.empty or len(equity_series) < 10:
        return {}
    
    total_days = (equity_series.index[-1] - equity_series.index[0]).days
    years = max(total_days / 365.25, 0.1)
    
    init_val = equity_series.iloc[0]
    final_val = equity_series.iloc[-1]
    total_ret = (final_val / init_val) - 1.0
    cagr = ((final_val / init_val) ** (1.0 / years)) - 1.0
    
    daily_rets = equity_series.pct_change().dropna()
    mean_ret = daily_rets.mean() * 252
    vol = daily_rets.std() * np.sqrt(252)
    sharpe = (mean_ret - risk_free) / (vol + 1e-9) if vol > 0 else 0.0
    
    cummax = equity_series.cummax()
    drawdown = (equity_series - cummax) / cummax
    max_dd = drawdown.min()
    calmar = cagr / abs(max_dd) if abs(max_dd) > 0 else 0.0
    
    downside = daily_rets[daily_rets < 0]
    downside_vol = downside.std() * np.sqrt(252)
    sortino = (mean_ret - risk_free) / (downside_vol + 1e-9) if downside_vol > 0 else 0.0
    
    return {
        'Total_Return_Pct': round(total_ret * 100.0, 2),
        'CAGR_Pct': round(cagr * 100.0, 2),
        'Annualized_Vol_Pct': round(vol * 100.0, 2),
        'Sharpe_Ratio': round(sharpe, 2),
        'Sortino_Ratio': round(sortino, 2),
        'Max_Drawdown_Pct': round(max_dd * 100.0, 2),
        'Calmar_Ratio': round(calmar, 2),
        'Years': round(years, 1)
    }

def backtest_halloween_effect(df: pd.DataFrame, daily_rf: float = 0.02 / 252):
    """
    Estrategia Halloween / 'Sell in May and Go Away':
    - Largo de Noviembre a Abril (Meses 11, 12, 1, 2, 3, 4).
    - En Liquidez / Renta Fija de Mayo a Octubre (Meses 5, 6, 7, 8, 9, 10).
    """
    df = df.copy()
    df['Month'] = df.index.month
    df['Market_Ret'] = df['Close'].pct_change().fillna(0)
    
    # 1. Halloween (Nov-Apr)
    df['Halloween_Signal'] = df['Month'].isin([11, 12, 1, 2, 3, 4]).astype(int)
    df['Halloween_Ret'] = np.where(df['Halloween_Signal'] == 1, df['Market_Ret'], daily_rf)
    df['Halloween_Equity'] = (1.0 + df['Halloween_Ret']).cumprod() * 100000.0
    
    # 2. Inverso Halloween (May-Oct)
    df['Summer_Signal'] = df['Month'].isin([5, 6, 7, 8, 9, 10]).astype(int)
    df['Summer_Ret'] = np.where(df['Summer_Signal'] == 1, df['Market_Ret'], daily_rf)
    df['Summer_Equity'] = (1.0 + df['Summer_Ret']).cumprod() * 100000.0
    
    # 3. Buy & Hold Benchmark
    df['BH_Equity'] = (1.0 + df['Market_Ret']).cumprod() * 100000.0
    
    m_hallow = compute_metrics(df['Halloween_Equity'])
    m_summer = compute_metrics(df['Summer_Equity'])
    m_bh = compute_metrics(df['BH_Equity'])
    
    return df, m_hallow, m_summer, m_bh

def backtest_turn_of_the_month(df: pd.DataFrame, daily_rf: float = 0.02 / 252):
    """
    Turn-of-the-Month (TOTM):
    Largo únicamente el último día del mes y los primeros 4 días hábiles del nuevo mes (~5 días/mes).
    Resto del mes en liquidez (50% menos exposición al mercado).
    """
    df = df.copy()
    df['Market_Ret'] = df['Close'].pct_change().fillna(0)
    
    # Detectar día de mes hábil
    df['Month'] = df.index.month
    df['Month_Change'] = (df['Month'] != df['Month'].shift(-1)).astype(int) # Último día del mes
    
    # Asignar ranking de día del mes
    day_in_month = []
    cur_m = None
    c_day = 0
    for dt in df.index:
        if dt.month != cur_m:
            cur_m = dt.month
            c_day = 1
        else:
            c_day += 1
        day_in_month.append(c_day)
    df['Trading_Day_Of_Month'] = day_in_month
    
    # Señal TOTM: Último día del mes O primeros 4 días del mes
    df['TOTM_Signal'] = ((df['Month_Change'] == 1) | (df['Trading_Day_Of_Month'] <= 4)).astype(int)
    df['TOTM_Ret'] = np.where(df['TOTM_Signal'] == 1, df['Market_Ret'], daily_rf)
    df['TOTM_Equity'] = (1.0 + df['TOTM_Ret']).cumprod() * 100000.0
    
    # Resto del mes
    df['Rest_Ret'] = np.where(df['TOTM_Signal'] == 0, df['Market_Ret'], daily_rf)
    df['Rest_Equity'] = (1.0 + df['Rest_Ret']).cumprod() * 100000.0
    
    m_totm = compute_metrics(df['TOTM_Equity'])
    m_rest = compute_metrics(df['Rest_Equity'])
    return df, m_totm, m_rest

def analyze_monthly_performance(df: pd.DataFrame):
    """Calcula el rendimiento medio, mediano, tasa de acierto y distribución por mes."""
    df_m = df['Close'].resample('ME').last().pct_change().dropna()
    df_m_stats = []
    
    month_names = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    for m in range(1, 13):
        m_rets = df_m[df_m.index.month == m] * 100.0
        n_years = len(m_rets)
        pos = (m_rets > 0).sum()
        win_rate = (pos / n_years) * 100.0 if n_years > 0 else 0.0
        
        df_m_stats.append({
            'Mes_Num': m,
            'Mes': month_names[m],
            'Retorno_Medio_Pct': round(m_rets.mean(), 2),
            'Retorno_Mediano_Pct': round(m_rets.median(), 2),
            'Win_Rate_Pct': round(win_rate, 1),
            'Mejor_Mes_Pct': round(m_rets.max(), 2),
            'Peor_Mes_Pct': round(m_rets.min(), 2),
            'Anios_Totales': n_years
        })
    return pd.DataFrame(df_m_stats)

def main():
    print("=" * 80)
    print("TRADINGVOLT QUANTITATIVE RESEARCH • AUDITORÍA DE ESTACIONALIDAD")
    print("=" * 80)

    # 1. S&P 500 (SPY desde 1993 - 33 años)
    print("\nDescargando datos históricos de SPY (1993-2026)...")
    spy_raw = yf.download("SPY", start="1993-01-01", end="2026-11-01", progress=False, threads=False)
    if isinstance(spy_raw.columns, pd.MultiIndex):
        spy_raw.columns = spy_raw.columns.get_level_values(0)
    spy_df = spy_raw.dropna(subset=['Close'])

    print(f"Total sesiones analizadas en SPY: {len(spy_df):,} sesiones ({spy_df.index[0].strftime('%Y-%m-%d')} a {spy_df.index[-1].strftime('%Y-%m-%d')})")

    # A) Halloween Effect (Sell in May)
    _, m_hallow, m_summer, m_bh = backtest_halloween_effect(spy_df)

    print("\n" + "-" * 75)
    print("1. EFECTO HALLOWEEN / 'SELL IN MAY AND GO AWAY' EN S&P 500 (SPY)")
    print("-" * 75)
    df_hallow_comp = pd.DataFrame([
        {'Estrategia': '[HALLOWEEN] Invierno (Nov-Abr)', **m_hallow, 'Exposicion': '50% tiempo'},
        {'Estrategia': '[SUMMER] Verano (May-Oct)', **m_summer, 'Exposicion': '50% tiempo'},
        {'Estrategia': '[BUY_HOLD] S&P 500 Todo el ano', **m_bh, 'Exposicion': '100% tiempo'}
    ])
    cols_h = ['Estrategia', 'CAGR_Pct', 'Max_Drawdown_Pct', 'Sharpe_Ratio', 'Sortino_Ratio', 'Exposicion']
    print(df_hallow_comp[cols_h].to_string(index=False))

    # B) Turn-of-the-Month (TOTM)
    _, m_totm, m_rest = backtest_turn_of_the_month(spy_df)
    print("\n" + "-" * 75)
    print("2. EFECTO CAMBIO DE MES (TURN-OF-THE-MONTH: ULTIMO DIA + PRIMEROS 4 DIAS)")
    print("-" * 75)
    df_totm_comp = pd.DataFrame([
        {'Estrategia': '[TOTM] Turn of Month (5 dias/mes)', **m_totm, 'Exposicion': '~24% tiempo'},
        {'Estrategia': '[REST] Resto del Mes (16 dias/mes)', **m_rest, 'Exposicion': '~76% tiempo'},
        {'Estrategia': '[BUY_HOLD] S&P 500 Todo el ano', **m_bh, 'Exposicion': '100% tiempo'}
    ])
    print(df_totm_comp[cols_h].to_string(index=False))

    # C) Desglose Mensual SPY
    df_m_spy = analyze_monthly_performance(spy_df)
    print("\n" + "-" * 75)
    print("3. DESGLOSE MENSUAL HISTORICO DE SPY (1993 - 2026)")
    print("-" * 75)
    print(df_m_spy[['Mes', 'Retorno_Medio_Pct', 'Retorno_Mediano_Pct', 'Win_Rate_Pct', 'Mejor_Mes_Pct', 'Peor_Mes_Pct']].to_string(index=False))

    # D) Nasdaq 100 (QQQ desde 1999)
    print("\n" + "-" * 75)
    print("4. EFECTO HALLOWEEN EN NASDAQ 100 (QQQ - 1999 A 2026)")
    print("-" * 75)
    qqq_raw = yf.download("QQQ", start="1999-01-01", end="2026-11-01", progress=False, threads=False)
    if isinstance(qqq_raw.columns, pd.MultiIndex):
        qqq_raw.columns = qqq_raw.columns.get_level_values(0)
    qqq_df = qqq_raw.dropna(subset=['Close'])
    _, m_h_qqq, m_s_qqq, m_bh_qqq = backtest_halloween_effect(qqq_df)
    df_qqq_comp = pd.DataFrame([
        {'Estrategia': '[HALLOWEEN] QQQ Invierno (Nov-Abr)', **m_h_qqq},
        {'Estrategia': '[SUMMER] QQQ Verano (May-Oct)', **m_s_qqq},
        {'Estrategia': '[BUY_HOLD] QQQ Todo el ano', **m_bh_qqq}
    ])
    print(df_qqq_comp[['Estrategia', 'CAGR_Pct', 'Max_Drawdown_Pct', 'Sharpe_Ratio', 'Sortino_Ratio']].to_string(index=False))

    # E) Estacionalidad en Commodities
    print("\n" + "-" * 75)
    print("5. ESTACIONALIDAD ESPECIFICA EN COMMODITIES")
    print("-" * 75)
    # Petroleo: Febrero a Junio (Driving season)
    cl_raw = yf.download("CL=F", start="2000-01-01", end="2026-11-01", progress=False, threads=False)
    if isinstance(cl_raw.columns, pd.MultiIndex): cl_raw.columns = cl_raw.columns.get_level_values(0)
    cl_df = cl_raw.dropna(subset=['Close'])
    cl_df['Month'] = cl_df.index.month
    cl_df['Market_Ret'] = cl_df['Close'].pct_change().fillna(0)
    cl_df['Oil_Seasonal_Ret'] = np.where(cl_df['Month'].isin([2, 3, 4, 5, 6]), cl_df['Market_Ret'], 0.02/252)
    cl_df['Oil_Off_Ret'] = np.where(cl_df['Month'].isin([7, 8, 9, 10, 11, 12, 1]), cl_df['Market_Ret'], 0.02/252)
    m_cl_sea = compute_metrics((1.0 + cl_df['Oil_Seasonal_Ret']).cumprod() * 100000.0)
    m_cl_off = compute_metrics((1.0 + cl_df['Oil_Off_Ret']).cumprod() * 100000.0)
    m_cl_bh = compute_metrics((1.0 + cl_df['Market_Ret']).cumprod() * 100000.0)

    # Oro: Diciembre a Febrero y Julio a Septiembre
    gc_raw = yf.download("GC=F", start="2000-01-01", end="2026-11-01", progress=False, threads=False)
    if isinstance(gc_raw.columns, pd.MultiIndex): gc_raw.columns = gc_raw.columns.get_level_values(0)
    gc_df = gc_raw.dropna(subset=['Close'])
    gc_df['Month'] = gc_df.index.month
    gc_df['Market_Ret'] = gc_df['Close'].pct_change().fillna(0)
    gc_df['Gold_Seasonal_Ret'] = np.where(gc_df['Month'].isin([12, 1, 2, 7, 8, 9]), gc_df['Market_Ret'], 0.02/252)
    gc_df['Gold_Off_Ret'] = np.where(~gc_df['Month'].isin([12, 1, 2, 7, 8, 9]), gc_df['Market_Ret'], 0.02/252)
    m_gc_sea = compute_metrics((1.0 + gc_df['Gold_Seasonal_Ret']).cumprod() * 100000.0)
    m_gc_off = compute_metrics((1.0 + gc_df['Gold_Off_Ret']).cumprod() * 100000.0)
    m_gc_bh = compute_metrics((1.0 + gc_df['Market_Ret']).cumprod() * 100000.0)

    df_comm = pd.DataFrame([
        {'Activo / Estrategia': '[OIL] Petroleo (Feb-Jun Driving Season)', **m_cl_sea},
        {'Activo / Estrategia': '[OIL] Petroleo Fuera de Estacion (Jul-Ene)', **m_cl_off},
        {'Activo / Estrategia': '[OIL] Petroleo Buy & Hold (CL=F)', **m_cl_bh},
        {'Activo / Estrategia': '[GOLD] Oro Ventana Estacional (Dic-Feb + Jul-Sep)', **m_gc_sea},
        {'Activo / Estrategia': '[GOLD] Oro Fuera de Estacion (Mar-Jun + Oct-Nov)', **m_gc_off},
        {'Activo / Estrategia': '[GOLD] Oro Buy & Hold (GC=F)', **m_gc_bh}
    ])
    print(df_comm[['Activo / Estrategia', 'CAGR_Pct', 'Max_Drawdown_Pct', 'Sharpe_Ratio']].to_string(index=False))

if __name__ == "__main__":
    main()
