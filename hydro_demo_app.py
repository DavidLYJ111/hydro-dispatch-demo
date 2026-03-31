import time
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="智调水电Demo", layout="wide")


def inject_dashboard_css():
    if "play_hour" not in st.session_state:
        st.session_state.play_hour = 0
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = False

    if "demo_hour" not in st.session_state:
        st.session_state.demo_hour = 0

    if "demo_strategy_idx" not in st.session_state:
        st.session_state.demo_strategy_idx = 0

    st.markdown("""
    <style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(110, 191, 255, 0.18), transparent 28%),
            radial-gradient(circle at top right, rgba(116, 255, 214, 0.12), transparent 24%),
            linear-gradient(180deg, #edf6ff 0%, #dff0ff 45%, #d7ebfb 100%);
        color: #17324d;
    }

    .block-container {
        padding-top: 1.0rem;
        padding-bottom: 1.0rem;
        max-width: 100%;
    }

    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b223a 0%, #123250 100%);
        border-right: 1px solid rgba(90, 170, 255, 0.20);
    }

    /* ⭐ 只控制普通文本，不影响输入控件 */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    /* ⭐ 只控制文字，不碰结构容器 */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #eef7ff;
    }

    .dashboard-title {
        padding: 16px 20px;
        border: 1px solid rgba(102, 168, 232, 0.30);
        border-radius: 18px;
        background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(241,248,255,0.90));
        box-shadow: 0 10px 28px rgba(53, 126, 189, 0.12);
        margin-bottom: 12px;
    }

    .dashboard-title h1 {
        margin: 0;
        font-size: 30px;
        font-weight: 800;
        letter-spacing: 0.6px;
        color: #0f3b63;
    }

    .dashboard-title p {
        margin: 6px 0 0 0;
        color: #4f769a;
        font-size: 14px;
    }

    .panel-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(243,249,255,0.92));
        border: 1px solid rgba(103, 173, 235, 0.28);
        border-radius: 18px;
        padding: 14px 14px 10px 14px;
        box-shadow: 0 10px 24px rgba(54, 122, 183, 0.10);
        margin-bottom: 12px;
    }

    .panel-title {
        font-size: 15px;
        font-weight: 800;
        color: #0d5588;
        margin-bottom: 10px;
        letter-spacing: 0.3px;
    }

    .status-chip-wrap {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
        margin-top: 10px;
    }

    .status-chip {
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(112, 192, 255, 0.10);
        border: 1px solid rgba(93, 171, 236, 0.28);
        color: #27597f;
        font-size: 12px;
        font-weight: 600;
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(244,249,255,0.94));
        border: 1px solid rgba(98, 170, 235, 0.25);
        border-radius: 16px;
        padding: 10px 12px;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.35), 0 8px 20px rgba(62, 129, 189, 0.08);
    }

    div[data-testid="metric-container"] label {
        color: #5a7ea0 !important;
        font-weight: 600;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #183a59 !important;
    }

    .main-3d-wrap {
        background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(243,249,255,0.92));
        border: 1px solid rgba(102, 170, 232, 0.28);
        border-radius: 20px;
        padding: 14px;
        box-shadow: 0 10px 24px rgba(54, 122, 183, 0.10);
        margin-bottom: 12px;
    }

    .main-3d-title {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0;
    }

    .main-3d-title-left {
        font-size: 17px;
        font-weight: 800;
        color: #0f4f80;
        letter-spacing: 0.3px;
    }

    .main-3d-title-right {
        font-size: 12px;
        color: #4f769a;
        background: rgba(122, 196, 255, 0.10);
        border: 1px solid rgba(102, 170, 232, 0.24);
        border-radius: 999px;
        padding: 5px 10px;
    }

    .chart-panel {
        background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(243,249,255,0.92));
        border: 1px solid rgba(102, 170, 232, 0.24);
        border-radius: 18px;
        padding: 10px 10px 4px 10px;
        margin-top: 10px;
        box-shadow: 0 8px 22px rgba(54, 122, 183, 0.08);
    }

    .stAlert {
        border-radius: 14px;
    }

    .stDataFrame, .stTable {
        border-radius: 14px;
        overflow: hidden;
    }

    hr {
        border-color: rgba(102, 170, 232, 0.20);
    }

    .element-container iframe {
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(102, 170, 232, 0.24);
        box-shadow: 0 10px 24px rgba(54, 122, 183, 0.10);
        background: #eef7ff;
    }
     /* ⭐ 修复输入框/选择框文字看不见 */
    section[data-testid="stSidebar"] input,
    section[data-testid="stSidebar"] select,
    section[data-testid="stSidebar"] textarea {
        color: #0b223a !important;   /* 深色字 */
        background-color: #ffffff !important;
    }

    /* ⭐ slider 数值颜色 */
    section[data-testid="stSidebar"] .stSlider div {
        color: #ffffff !important;
    }   

     /* ⭐ 修复 selectbox（当前策略）文字颜色 */
    section[data-testid="stSidebar"] div[role="combobox"] {
        color: #0b223a !important;
        background-color: #ffffff !important;
    }

    /* ⭐ 下拉展开后的选项 */
    section[data-testid="stSidebar"] div[role="listbox"] {
        color: #0b223a !important;
    }

    /* ⭐ 选中项文本 */
    section[data-testid="stSidebar"] div[role="combobox"] span {
        color: #0b223a !important;
    }

    /* ⭐ 强制修复 selectbox 当前显示文字 */
    section[data-testid="stSidebar"] div[role="combobox"] * {
        color: #0b223a !important;
    }

    /* ⭐ 重点：锁定真正显示文字的 span */
    section[data-testid="stSidebar"] div[role="combobox"] span {
        color: #0b223a !important;
    }

    /* ⭐ 输入状态（光标输入时） */
    section[data-testid="stSidebar"] input {
        color: #0b223a !important;
    }

    /* ⭐ 下拉菜单 */
    section[data-testid="stSidebar"] div[role="listbox"] * {
        color: #0b223a !important;
    }

    /* ⭐ 背景统一 */
    section[data-testid="stSidebar"] div[role="combobox"] {
        background-color: #ffffff !important;
    }

    /* ⭐ 侧边栏标题统一变白 */
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4 {
        color: #ffffff !important;
    }

    /* ⭐ 演示按钮可见性修复 */
    section[data-testid="stSidebar"] button {
        background-color: #1f4e79 !important;
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.3) !important;
    }

    /* ⭐ hover效果 */
    section[data-testid="stSidebar"] button:hover {
        background-color: #2f6fa5 !important;
        color: #ffffff !important;
    }

    </style>
    """, unsafe_allow_html=True)


# =========================================================
# 1. 数据与模型
# =========================================================
def make_synthetic_inputs(seed=42):
    rng = np.random.default_rng(seed)
    hours = np.arange(24)

    inflow = 120 + 40 * np.sin((hours - 6) / 24 * 2 * np.pi) + rng.normal(0, 5, size=24)
    inflow = np.clip(inflow, 60, 200)

    price = (
            200
            + 120 * np.exp(-0.5 * ((hours - 19) / 3) ** 2)
            + 40 * np.exp(-0.5 * ((hours - 10) / 4) ** 2)
            + rng.normal(0, 5, size=24)
    )
    price = np.clip(price, 100, 450)

    return inflow, price


def simulate_schedule(Q, inflow, price, params):
    rho = 1000.0
    g = 9.81

    Q = np.asarray(Q, dtype=float).copy()
    inflow = np.asarray(inflow, dtype=float)
    price = np.asarray(price, dtype=float)

    S0 = params["S0"]
    S_min = params["S_min"]
    S_max = params["S_max"]
    Q_min = params["Q_min"]
    Q_max = params["Q_max"]
    head = params["head"]
    eta = params["eta"]
    alpha_spill = params["alpha_spill"]
    beta_smooth = params["beta_smooth"]
    k_storage = params["k_storage"]
    penalty_big = params["penalty_big"]

    Q = np.clip(Q, 0.0, Q_max)

    S = np.zeros(25)
    S[0] = S0

    spill = 0.0
    penalty = 0.0
    power_mw = np.zeros(24)
    revenue_hour = np.zeros(24)

    for t in range(24):
        if Q[t] < Q_min:
            penalty += penalty_big * (Q_min - Q[t]) ** 2

        S[t + 1] = S[t] + k_storage * (inflow[t] - Q[t])

        if S[t + 1] > S_max:
            overflow = S[t + 1] - S_max
            spill += overflow
            S[t + 1] = S_max

        if S[t + 1] < S_min:
            penalty += penalty_big * (S_min - S[t + 1]) ** 2

        power_mw[t] = (rho * g * Q[t] * head * eta) / 1e6
        revenue_hour[t] = power_mw[t] * price[t]

    smooth_penalty = float(np.sum((Q[1:] - Q[:-1]) ** 2))
    revenue = float(np.sum(revenue_hour))
    obj = revenue - alpha_spill * spill - beta_smooth * smooth_penalty - penalty

    detail = {
        "S": S,
        "power_mw": power_mw,
        "revenue_hour": revenue_hour,
        "cum_revenue": np.cumsum(revenue_hour),
        "revenue": revenue,
        "spill": spill,
        "smooth_penalty": smooth_penalty,
        "penalty": penalty,
        "objective": obj,
    }
    return obj, detail


# =========================================================
# 2. 调度方法
# =========================================================
def rule_based_schedule(inflow, price, params):
    inflow = np.asarray(inflow, dtype=float)
    price = np.asarray(price, dtype=float)

    Q_min = params["Q_min"]
    Q_max = params["Q_max"]
    S0 = params["S0"]
    S_min = params["S_min"]
    S_max = params["S_max"]
    k_storage = params["k_storage"]

    hours = len(inflow)
    Q = np.zeros(hours)
    S = np.zeros(hours + 1)
    S[0] = S0

    price_mean = np.mean(price)
    price_std = np.std(price) + 1e-6

    for t in range(hours):
        q_base = 0.98 * inflow[t]
        price_z = (price[t] - price_mean) / price_std
        q_price = 40.0 * price_z
        storage_ratio = (S[t] - S_min) / (S_max - S_min + 1e-6)
        q_storage = 55.0 * (storage_ratio - 0.5)

        q = q_base + q_price + q_storage
        q = np.clip(q, Q_min, Q_max)

        if t > 0:
            q = 0.7 * Q[t - 1] + 0.3 * q

        Q[t] = q
        S[t + 1] = S[t] + k_storage * (inflow[t] - Q[t])
        S[t + 1] = np.clip(S[t + 1], S_min, S_max)

    return Q


def pso_optimize(inflow, price, params, n_particles=30, n_iters=50, w=0.7, c1=1.6, c2=1.6, seed=2):
    rng = np.random.default_rng(seed)
    dim = 24
    Q_min = params["Q_min"]
    Q_max = params["Q_max"]

    X = rng.uniform(Q_min, Q_max, size=(n_particles, dim))
    V = rng.normal(0, 10, size=(n_particles, dim))

    def f(x):
        return simulate_schedule(x, inflow, price, params)[0]

    pbest = X.copy()
    pbest_val = np.array([f(x) for x in X], dtype=float)

    gbest_idx = int(np.argmax(pbest_val))
    gbest = pbest[gbest_idx].copy()
    gbest_val = float(pbest_val[gbest_idx])

    history = []

    for _ in range(n_iters):
        r1 = rng.random((n_particles, dim))
        r2 = rng.random((n_particles, dim))

        V = w * V + c1 * r1 * (pbest - X) + c2 * r2 * (gbest - X)
        X = np.clip(X + V, Q_min, Q_max)

        vals = np.array([f(x) for x in X], dtype=float)
        improved = vals > pbest_val
        pbest[improved] = X[improved]
        pbest_val[improved] = vals[improved]

        best_idx = int(np.argmax(pbest_val))
        if pbest_val[best_idx] > gbest_val:
            gbest_val = float(pbest_val[best_idx])
            gbest = pbest[best_idx].copy()

        history.append(gbest_val)

    return gbest, gbest_val, np.array(history)


def apso_ls_optimize(
        inflow, price, params,
        n_particles=30, n_iters=50,
        w_max=0.95, w_min=0.45, decay_k=3.0,
        c1=1.6, c2=1.6,
        stagnation_window=8,
        w_boost=0.12,
        v_clip=30.0,
        seed=3,
        ls_trials=80,
        ls_sigma=6.0,
):
    rng = np.random.default_rng(seed)
    dim = 24
    Q_min = params["Q_min"]
    Q_max = params["Q_max"]

    def f(x):
        return simulate_schedule(x, inflow, price, params)[0]

    X = rng.uniform(Q_min, Q_max, size=(n_particles, dim))
    V = rng.normal(0, 10, size=(n_particles, dim))

    pbest = X.copy()
    pbest_val = np.array([f(x) for x in X], dtype=float)

    gbest_idx = int(np.argmax(pbest_val))
    gbest = pbest[gbest_idx].copy()
    gbest_val = float(pbest_val[gbest_idx])

    history = []
    no_improve = 0

    for it in range(n_iters):
        t = it / max(1, n_iters - 1)
        w = w_min + (w_max - w_min) * np.exp(-decay_k * t)

        if no_improve >= stagnation_window:
            w = min(w_max, w + w_boost)

        r1 = rng.random((n_particles, dim))
        r2 = rng.random((n_particles, dim))

        V = w * V + c1 * r1 * (pbest - X) + c2 * r2 * (gbest - X)
        V = np.clip(V, -v_clip, v_clip)
        X = np.clip(X + V, Q_min, Q_max)

        vals = np.array([f(x) for x in X], dtype=float)
        improved = vals > pbest_val
        pbest[improved] = X[improved]
        pbest_val[improved] = vals[improved]

        best_idx = int(np.argmax(pbest_val))
        if pbest_val[best_idx] > gbest_val:
            gbest_val = float(pbest_val[best_idx])
            gbest = pbest[best_idx].copy()
            no_improve = 0
        else:
            no_improve += 1

        history.append(gbest_val)

    best = gbest.copy()
    best_val = gbest_val
    for _ in range(ls_trials):
        cand = best + rng.normal(0, ls_sigma, size=dim)
        cand = np.clip(cand, Q_min, Q_max)
        val = float(f(cand))
        if val > best_val:
            best_val = val
            best = cand

    return best, best_val, np.array(history)


def ga_optimize(
        inflow, price, params,
        pop_size=40, n_gens=50,
        cx_prob=0.9, mut_prob=0.25, mut_sigma=10.0,
        elite_k=2, seed=7
):
    rng = np.random.default_rng(seed)
    dim = 24
    Q_min = params["Q_min"]
    Q_max = params["Q_max"]

    def fitness(x):
        return simulate_schedule(x, inflow, price, params)[0]

    pop = rng.uniform(Q_min, Q_max, size=(pop_size, dim))
    fit = np.array([fitness(ind) for ind in pop], dtype=float)

    history = []

    def tournament_select(k=3):
        idx = rng.integers(0, pop_size, size=k)
        best = idx[np.argmax(fit[idx])]
        return pop[best].copy()

    for _ in range(n_gens):
        elite_idx = np.argsort(fit)[-elite_k:]
        elites = pop[elite_idx].copy()

        new_pop = []
        while len(new_pop) < pop_size - elite_k:
            p1 = tournament_select()
            p2 = tournament_select()

            if rng.random() < cx_prob:
                mask = rng.random(dim) < 0.5
                c1 = np.where(mask, p1, p2)
                c2 = np.where(mask, p2, p1)
            else:
                c1, c2 = p1.copy(), p2.copy()

            def mutate(child):
                if rng.random() < mut_prob:
                    child = child + rng.normal(0, mut_sigma, size=dim)
                return np.clip(child, Q_min, Q_max)

            c1 = mutate(c1)
            c2 = mutate(c2)

            new_pop.append(c1)
            if len(new_pop) < pop_size - elite_k:
                new_pop.append(c2)

        pop = np.vstack([np.array(new_pop), elites])
        fit = np.array([fitness(ind) for ind in pop], dtype=float)
        history.append(float(np.max(fit)))

    best_idx = int(np.argmax(fit))
    best = pop[best_idx].copy()
    best_val = float(fit[best_idx])
    return best, best_val, np.array(history)


# =========================================================
# 3. 绘图
# =========================================================
def build_reservoir_scene_2d(storage, params, release, inflow, power, hour):
    s_min = params["S_min"]
    s_max = params["S_max"]
    level_ratio = (storage - s_min) / (s_max - s_min)
    level_ratio = float(np.clip(level_ratio, 0.08, 0.98))
    water_y = 20 + 24 * level_ratio

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[0, 10, 22, 38, 54, 70, 86, 100, 100, 0],
        y=[80, 92, 78, 94, 76, 90, 82, 96, 0, 0],
        fill="toself",
        mode="lines",
        line=dict(color="#a77c45", width=2),
        fillcolor="rgba(181, 146, 92, 0.55)",
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[0, 12, 24, 76, 88, 100, 100, 0],
        y=[0, 18, 34, 34, 18, 0, -2, -2],
        fill="toself",
        mode="lines",
        line=dict(color="#7daa52", width=2),
        fillcolor="rgba(136, 179, 96, 0.70)",
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[16, 26, 74, 84, 84, 16],
        y=[water_y - 3, water_y, water_y, water_y - 3, 8, 8],
        fill="toself",
        mode="lines",
        line=dict(color="#36a9e1", width=2),
        fillcolor="rgba(88, 194, 244, 0.75)",
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[26, 74, 80, 20],
        y=[water_y - 1, water_y - 1, water_y - 4, water_y - 4],
        fill="toself",
        mode="lines",
        line=dict(color="rgba(255,255,255,0)"),
        fillcolor="rgba(180, 235, 255, 0.18)",
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[72, 86, 88, 74],
        y=[14, 14, 54, 54],
        fill="toself",
        mode="lines",
        line=dict(color="#7f8894", width=2),
        fillcolor="rgba(160, 166, 174, 0.96)",
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[86, 90, 92, 88],
        y=[14, 18, 58, 54],
        fill="toself",
        mode="lines",
        line=dict(color="#6d7682", width=1.5),
        fillcolor="rgba(120, 128, 138, 0.92)",
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[74, 88],
        y=[54, 54],
        mode="lines",
        line=dict(color="#cfd6de", width=3),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[67, 72, 72, 67, 67],
        y=[10, 10, 16, 16, 10],
        fill="toself",
        mode="lines",
        line=dict(color="#8b5a2b", width=1.5),
        fillcolor="rgba(210, 170, 110, 0.95)",
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[24, 71],
        y=[water_y, water_y],
        mode="lines",
        line=dict(color="#1f77b4", width=2, dash="dash"),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_trace(go.Scatter(
        x=[88.5, 88.5],
        y=[28, 40],
        mode="lines",
        line=dict(color="#2f9bff", width=5),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig.add_annotation(
        x=15, y=12, ax=4, ay=12,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=3, arrowcolor="#2fb344"
    )
    fig.add_annotation(x=10, y=7, text="入流", showarrow=False, font=dict(size=11, color="#1f7a1f"))

    fig.add_annotation(
        x=90, y=30, ax=99, ay=30,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True, arrowhead=3, arrowsize=1.5, arrowwidth=3, arrowcolor="#2f9bff"
    )
    fig.add_annotation(x=95, y=34, text="泄流", showarrow=False, font=dict(size=11, color="#1f6ed4"))

    fig.add_annotation(x=50, y=28, text="某某河水库", showarrow=False, font=dict(size=22, color="#0f3b63"))
    fig.add_annotation(
        x=12, y=66,
        text=f"第 {hour:02d} 时<br>水位比例: {level_ratio:.2f}",
        showarrow=False,
        align="left",
        font=dict(size=13, color="#ffffff"),
        bgcolor="rgba(0,0,0,0.35)",
        bordercolor="rgba(255,255,255,0.15)",
        borderwidth=1
    )
    fig.add_annotation(
        x=47, y=water_y + 3,
        text="坝前水位线",
        showarrow=False,
        font=dict(size=11, color="#1f77b4"),
        bgcolor="rgba(255,255,255,0.65)"
    )
    fig.add_annotation(
        x=69.5, y=18.5,
        text="厂房",
        showarrow=False,
        font=dict(size=11, color="#8b5a2b"),
        bgcolor="rgba(255,255,255,0.65)"
    )
    fig.add_annotation(
        x=84.5, y=43,
        text="泄洪闸门",
        showarrow=False,
        font=dict(size=11, color="#1f6ed4"),
        bgcolor="rgba(255,255,255,0.65)"
    )

    fig.update_layout(
        height=430,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="rgba(240,248,255,0.9)",
        xaxis=dict(range=[0, 100], visible=False),
        yaxis=dict(range=[0, 95], visible=False, scaleanchor="x", scaleratio=1),
        showlegend=False,
        hovermode=False
    )
    return fig


def apply_clean_layout(fig, title, x_title, y_title, height=280):
    fig.update_layout(
        title=title,
        height=height,
        margin=dict(l=20, r=20, t=42, b=20),
        paper_bgcolor="white",
        plot_bgcolor="rgba(245,249,255,1)",
        font=dict(color="#1f2d3d"),
        xaxis=dict(
            title=x_title,
            gridcolor="rgba(120,140,170,0.18)",
            zerolinecolor="rgba(120,140,170,0.18)",
        ),
        yaxis=dict(
            title=y_title,
            gridcolor="rgba(120,140,170,0.18)",
            zerolinecolor="rgba(120,140,170,0.18)",
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.7)",
            bordercolor="rgba(0,0,0,0.08)"
        )
    )
    return fig


def build_reservoir_scene(storage, params, release, inflow, power, hour):
    s_min = params["S_min"]
    s_max = params["S_max"]

    level_ratio = (storage - s_min) / (s_max - s_min)
    level_ratio = float(np.clip(level_ratio, 0.08, 0.98))

    x = np.linspace(-10, 10, 70)
    y = np.linspace(-6, 16, 90)
    X, Y = np.meshgrid(x, y)

    valley = 0.18 * (X ** 2) + 0.015 * (Y - 4) ** 2
    slope = 0.18 * (16 - Y)
    Z_terrain = 26 + valley + slope

    channel = np.exp(-(X / 2.4) ** 2) * (5.5 + 0.12 * (16 - Y))
    Z_terrain = Z_terrain - channel

    water_level = 29 + 7.5 * level_ratio
    water_mask = (np.abs(X) < 3.2 + 0.05 * (16 - Y)) & (Y <= 12.2)
    Z_water = np.where(water_mask, water_level, np.nan)

    fig = go.Figure()

    fig.add_trace(go.Surface(
        x=X,
        y=Y,
        z=Z_terrain,
        colorscale=[
            [0.0, "#6ea04b"],
            [0.35, "#93b96a"],
            [0.55, "#b69568"],
            [0.75, "#9c7a52"],
            [1.0, "#7e6245"],
        ],
        showscale=False,
        opacity=1.0,
        hoverinfo="skip",
        name="地形"
    ))

    fig.add_trace(go.Surface(
        x=X,
        y=Y,
        z=Z_water,
        colorscale=[
            [0.0, "#9ddcff"],
            [0.5, "#58bff2"],
            [1.0, "#2f95d6"],
        ],
        showscale=False,
        opacity=0.88,
        hoverinfo="skip",
        name="库水"
    ))

    dam_vertices = np.array([
        [-2.2, 12.2, 24.5],
        [2.2, 12.2, 24.5],
        [-1.6, 12.2, 36.5],
        [1.6, 12.2, 36.5],
        [-2.8, 13.4, 23.8],
        [2.8, 13.4, 23.8],
        [-2.0, 13.4, 37.2],
        [2.0, 13.4, 37.2],
    ], dtype=float)

    i = [0, 0, 1, 2, 4, 4, 5, 6, 0, 0, 2, 2]
    j = [1, 2, 3, 3, 5, 6, 7, 7, 4, 2, 6, 3]
    k = [2, 4, 5, 1, 6, 0, 1, 5, 2, 6, 7, 7]

    fig.add_trace(go.Mesh3d(
        x=dam_vertices[:, 0],
        y=dam_vertices[:, 1],
        z=dam_vertices[:, 2],
        i=i, j=j, k=k,
        color="#a8b0ba",
        opacity=1.0,
        flatshading=True,
        hoverinfo="skip",
        name="坝体"
    ))

    house = np.array([
        [-3.2, 11.2, 23.5],
        [-1.6, 11.2, 23.5],
        [-3.2, 11.2, 26.2],
        [-1.6, 11.2, 26.2],
        [-3.2, 10.2, 23.5],
        [-1.6, 10.2, 23.5],
        [-3.2, 10.2, 26.2],
        [-1.6, 10.2, 26.2],
    ], dtype=float)

    i2 = [0, 0, 1, 2, 4, 4, 5, 6, 0, 0, 2, 2]
    j2 = [1, 2, 3, 3, 5, 6, 7, 7, 4, 2, 6, 3]
    k2 = [2, 4, 5, 1, 6, 0, 1, 5, 2, 6, 7, 7]

    fig.add_trace(go.Mesh3d(
        x=house[:, 0],
        y=house[:, 1],
        z=house[:, 2],
        i=i2, j=j2, k=k2,
        color="#c79c62",
        opacity=1.0,
        flatshading=True,
        hoverinfo="skip",
        name="厂房"
    ))

    fig.add_trace(go.Scatter3d(
        x=np.linspace(-2.6, 2.6, 40),
        y=np.full(40, 11.6),
        z=np.full(40, water_level),
        mode="lines",
        line=dict(color="#1f77b4", width=6, dash="dash"),
        hoverinfo="skip",
        showlegend=False
    ))

    fig.add_trace(go.Scatter3d(
        x=[0, 0, 0.0],
        y=[2.0, 0.0, -1.0],
        z=[water_level + 0.3, water_level + 0.3, water_level + 0.3],
        mode="lines",
        line=dict(color="#2fb344", width=8),
        hoverinfo="skip",
        showlegend=False
    ))

    fig.add_trace(go.Scatter3d(
        x=[0.4, 0.4, 0.4],
        y=[13.0, 15.0, 16.0],
        z=[29.0, 28.8, 28.5],
        mode="lines",
        line=dict(color="#2f9bff", width=8),
        hoverinfo="skip",
        showlegend=False
    ))

    fig.add_trace(go.Scatter3d(
        x=[0],
        y=[7.5],
        z=[water_level + 1.2],
        mode="text",
        text=[f"第 {hour:02d} 时<br>库水位比例: {level_ratio:.2f}"],
        textfont=dict(size=12, color="black"),
        hoverinfo="skip",
        showlegend=False
    ))

    fig.add_trace(go.Scatter3d(
        x=[0],
        y=[11.3],
        z=[water_level + 1.0],
        mode="text",
        text=["坝前水位线"],
        textfont=dict(size=11, color="#1f77b4"),
        hoverinfo="skip",
        showlegend=False
    ))

    fig.add_trace(go.Scatter3d(
        x=[-2.4],
        y=[10.7],
        z=[27.0],
        mode="text",
        text=["厂房"],
        textfont=dict(size=11, color="#8b5a2b"),
        hoverinfo="skip",
        showlegend=False
    ))

    fig.add_trace(go.Scatter3d(
        x=[1.2],
        y=[13.2],
        z=[34.0],
        mode="text",
        text=["泄洪闸门"],
        textfont=dict(size=11, color="#1f6ed4"),
        hoverinfo="skip",
        showlegend=False
    ))

    fig.update_layout(
        height=520,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="white",
        uirevision="keep-3d-camera",
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            bgcolor="rgba(240,248,255,1)",
            camera=dict(
                eye=dict(x=1.85, y=-2.35, z=1.15),
                center=dict(x=0.0, y=0.0, z=-0.05)
            ),
            aspectratio=dict(x=1.25, y=1.8, z=0.75),
        ),
        showlegend=False
    )
    return fig


def build_threejs_html(detail, Q, inflow, hour, auto_play):
    import json
    import base64

    t = int(hour)

    data_js = {
        "currentHour": t,
        "series": {
            "S": [float(x) for x in detail["S"][:-1]],
            "Q": [float(x) for x in Q],
            "inflow": [float(x) for x in inflow]
        }
    }

    data_str = json.dumps(data_js, ensure_ascii=False)

    def file_to_base64(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()

    glb_base64 = file_to_base64("gravity_dam.glb")
    terrain_diff_base64 = file_to_base64("textures/coast_sand_rocks_02_diff_4k.jpg")
    terrain_arm_base64 = file_to_base64("textures/coast_sand_rocks_02_arm_4k.jpg")
    water_normal_base64 = file_to_base64("water_normal.jpg")

    html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <style>
        html, body {
            margin: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #dfeaf4;
        }
        #app {
            width: 100%;
            height: 100%;
            position: relative;
            overflow: hidden;
        }
        #debugPanel {
            position: absolute;
            left: 18px;
            top: 18px;
            padding: 8px 10px;
            background: rgba(0,0,0,0.40);
            color: #fff;
            font-size: 13px;
            line-height: 1.5;
            border-radius: 6px;
            z-index: 20;
            pointer-events: none;
            min-width: 120px;
            font-family: Arial, sans-serif;
        }
        #errorPanel {
            position: absolute;
            left: 18px;
            bottom: 18px;
            max-width: 55%;
            padding: 8px 10px;
            background: rgba(180, 30, 30, 0.82);
            color: #fff;
            font-size: 12px;
            line-height: 1.4;
            border-radius: 6px;
            z-index: 30;
            display: none;
            white-space: pre-wrap;
            font-family: Consolas, monospace;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.134/examples/js/controls/OrbitControls.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.134/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
<div id="app">
    <div id="debugPanel"></div>
    <div id="errorPanel"></div>
</div>

<script>
(function () {

    function showError(msg) {
        try {
            const ep = document.getElementById("errorPanel");
            ep.style.display = "block";
            ep.textContent = String(msg);
        } catch (e) {
            console.error(msg);
        }
    }

    try {

        const DATA = """ + data_str + """;
        const GLB_BASE64 = '""" + glb_base64 + """';
        const TERRAIN_DIFFUSE = 'data:image/jpeg;base64,""" + terrain_diff_base64 + """';
        const TERRAIN_ARM = 'data:image/jpeg;base64,""" + terrain_arm_base64 + """';
        const WATER_NORMAL = 'data:image/jpeg;base64,""" + water_normal_base64 + """';

        const container = document.getElementById("app");
        const infoPanel = document.getElementById("debugPanel");

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xdfeaf4);
        scene.fog = new THREE.Fog(0xdfeaf4, 180, 420);

        const camera = new THREE.PerspectiveCamera(
            46,
            Math.max(1, container.clientWidth) / Math.max(1, container.clientHeight),
            0.1,
            2000
        );

        // 正对大坝的初始视角
        camera.position.set(150, 120, -20);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setPixelRatio(window.devicePixelRatio || 1);
        renderer.setSize(Math.max(1, container.clientWidth), Math.max(1, container.clientHeight));
        renderer.outputEncoding = THREE.sRGBEncoding;
        container.appendChild(renderer.domElement);

        const controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.08;
        controls.target.set(0, 13, 0);
        controls.minDistance = 35;
        controls.maxDistance = 260;
        controls.maxPolarAngle = Math.PI * 0.49;
        controls.update();

        const ambient = new THREE.AmbientLight(0xffffff, 0.86);
        scene.add(ambient);

        const sun = new THREE.DirectionalLight(0xffffff, 0.96);
        sun.position.set(120, 160, 80);
        scene.add(sun);

        const fill = new THREE.DirectionalLight(0xd8ebff, 0.30);
        fill.position.set(-100, 60, -90);
        scene.add(fill);

        const root = new THREE.Group();
        scene.add(root);

        const staticGroup = new THREE.Group();
        const dynamicGroup = new THREE.Group();
        root.add(staticGroup);
        root.add(dynamicGroup);

        const textureLoader = new THREE.TextureLoader();

        function prepareTexture(tex, repeatX, repeatY, isColor) {
            tex.wrapS = THREE.RepeatWrapping;
            tex.wrapT = THREE.RepeatWrapping;
            tex.repeat.set(repeatX, repeatY);
            tex.flipY = false;
            if (isColor) {
                tex.encoding = THREE.sRGBEncoding;
            }
            tex.anisotropy = Math.min(renderer.capabilities.getMaxAnisotropy(), 8);
            return tex;
        }

        const terrainDiffuseTex = prepareTexture(
            textureLoader.load(TERRAIN_DIFFUSE),
            10,
            7,
            true
        );

        const terrainArmTex = prepareTexture(
            textureLoader.load(TERRAIN_ARM),
            10,
            7,
            false
        );

        const waterNormalTex = prepareTexture(
            textureLoader.load(WATER_NORMAL),
            8,
            8,
            false
        );

        function clamp(v, a, b) {
            return Math.max(a, Math.min(b, v));
        }

        function lerp(a, b, t) {
            return a + (b - a) * t;
        }

        function smoothstep(a, b, x) {
            const t = clamp((x - a) / (b - a), 0.0, 1.0);
            return t * t * (3.0 - 2.0 * t);
        }

        function gauss(v, s) {
            return Math.exp(-(v * v) / (2.0 * s * s));
        }

        function waterLevelFromStorage(s) {
            const sMin = 20.0;
            const sMax = 55.0;
            const r = clamp((s - sMin) / (sMax - sMin), 0.0, 1.0);
            return 13.0 + r * 9.0;
        }

        function dischargeFactor(q) {
            return clamp((q - 30.0) / (220.0 - 30.0), 0.0, 1.0);
        }

        function getStateByHour(hour) {
            const n = DATA.series.Q.length;
            const h = clamp(Math.round(hour), 0, n - 1);

            const q = DATA.series.Q[h];
            const s = DATA.series.S[h];
            const inflow = DATA.series.inflow[h];

            const qFactor = dischargeFactor(q);
            const waterLevel = waterLevelFromStorage(s);

            return {
                hour: h,
                Q: q,
                S: s,
                inflow: inflow,
                qFactor: qFactor,
                waterLevel: waterLevel,
                flowOffsetX: 0.003 + qFactor * 0.004,
                flowOffsetY: 0.0015 + qFactor * 0.002,
                rippleRepeat: 16 + qFactor * 18
            };
        }

        let state = getStateByHour(DATA.currentHour);

        function updateInfoPanel() {
            infoPanel.innerHTML =
                "时刻: " + state.hour + "<br>" +
                "Q: " + state.Q.toFixed(1) + "<br>" +
                "S: " + state.S.toFixed(1) + "<br>" +
                "水位: " + state.waterLevel.toFixed(2);
        }

        waterNormalTex.repeat.set(state.rippleRepeat, state.rippleRepeat);

        function riverCenterZ(x) {
            if (x <= 0.0) return 0.0;
            return 0.05 * x;
        }

        function reservoirHalfWidth(x) {
            const t = smoothstep(-120.0, -6.0, x);
            return 42.0 - t * 22.0;
        }

        function riverHalfWidthBase(x) {
            const t = smoothstep(4.0, 120.0, x);

            const Q = state.Q;

            // ⭐ 在坝附近放大宽度
            const damBoost = Math.exp(-Math.pow((x - 5.0)/6.0, 2.0)) * 25;

            const widthQ = 0.3 * Math.sqrt(Q);

            return 8.0 + t * 12.0 + widthQ + damBoost;
        }

        function terrainHeight(x, z) {
            let y = 24.0;

            y += Math.sin(x * 0.022) * 2.2;
            y += Math.cos(z * 0.028) * 1.8;
            y += Math.sin((x + z) * 0.018) * 1.2;

            const basinCore = gauss(x + 62.0, 42.0) * gauss(z, 28.0);
            y -= basinCore * 12.0;

            const basinFlatten = gauss(x + 82.0, 55.0) * gauss(z, 42.0);
            y -= basinFlatten * 5.0;

            const throat = gauss(x + 3.0, 10.0) * gauss(z, 12.0);
            y -= throat * 16.0;

            if (x > 0.0) {
                const cz = riverCenterZ(x);
                const riverCut = Math.exp(-Math.pow((z - cz) / (10.0 + x * 0.05), 2.0));
                y -= riverCut * (10.0 + x * 0.06);
                y -= x * 0.12;
            }

            const leftWall = gauss(z + 38.0, 20.0) * 6.5;
            const rightWall = gauss(z - 38.0, 20.0) * 6.5;
            y += leftWall + rightWall;

            if (x < 0.0) {
                const shoreRaise = Math.pow(Math.abs(z) / 55.0, 1.5) * 4.0;
                y += shoreRaise;
            }

            return y;
        }

        function inReservoirMask(x, z) {
            const maskX = x >= -128.0 && x <= -4.0;
            const halfW = reservoirHalfWidth(x);
            const maskZ = Math.abs(z) <= halfW - 2.0;
            return maskX && maskZ;
        }

        const RIVER_PROFILE = [];

        function buildRiverProfile() {
            RIVER_PROFILE.length = 0;

            const startX = 2.0;
            const endX = 138.0;
            const step = 1.0;

            const startCenterZ = riverCenterZ(startX);
            const startBed = terrainHeight(startX, startCenterZ);

            let prevSurfaceY = Math.max(startBed + 1.2, state.waterLevel - 0.65);

            for (let x = startX; x <= endX + 1e-6; x += step) {
                const cz = riverCenterZ(x);
                const bedCenterY = terrainHeight(x, cz);

                const designSlope = 0.068 + state.qFactor * 0.020;
                const desiredSurfaceY = prevSurfaceY - designSlope * step;

                const Q = state.Q;

                const minDepth = 0.6 + 0.02 * Math.pow(Q, 0.4);
                const maxDepth = 2.5 + 0.08 * Math.pow(Q, 0.6);

                let surfaceY = clamp(desiredSurfaceY, bedCenterY + minDepth, bedCenterY + maxDepth);
                const drop = Math.exp(-Math.pow((x - 3.0)/4.0, 2.0)) * 1.2;
                surfaceY -= drop;

                surfaceY = Math.min(surfaceY, prevSurfaceY - 0.012);

                if (surfaceY < bedCenterY + minDepth) {
                    surfaceY = bedCenterY + minDepth;
                }

                const targetHalfW = riverHalfWidthBase(x);
                let wetHalfW = 1.8;

                for (let w = 1.8; w <= targetHalfW; w += 0.35) {
                    const zL = cz - w;
                    const zR = cz + w;
                    const bedL = terrainHeight(x, zL);
                    const bedR = terrainHeight(x, zR);

                    if (bedL <= surfaceY - 0.05 && bedR <= surfaceY - 0.05) {
                        wetHalfW = w;
                    } else {
                        break;
                    }
                }

                wetHalfW = Math.max(1.8, wetHalfW);

                RIVER_PROFILE.push({
                    x: x,
                    cz: cz,
                    y: surfaceY,
                    halfW: wetHalfW
                });

                prevSurfaceY = surfaceY;
            }
        }

        function sampleRiverProfile(x) {
            const n = RIVER_PROFILE.length;
            if (n === 0) {
                return {
                    cz: riverCenterZ(x),
                    y: terrainHeight(x, riverCenterZ(x)) + 0.5,
                    halfW: 2.5
                };
            }

            if (x <= RIVER_PROFILE[0].x) return RIVER_PROFILE[0];
            if (x >= RIVER_PROFILE[n - 1].x) return RIVER_PROFILE[n - 1];

            const baseX = RIVER_PROFILE[0].x;
            const i0 = clamp(Math.floor(x - baseX), 0, n - 1);
            const i1 = clamp(i0 + 1, 0, n - 1);

            const p0 = RIVER_PROFILE[i0];
            const p1 = RIVER_PROFILE[i1];

            const span = Math.max(1e-6, p1.x - p0.x);
            const t = clamp((x - p0.x) / span, 0.0, 1.0);

            return {
                cz: lerp(p0.cz, p1.cz, t),
                y: lerp(p0.y, p1.y, t),
                halfW: lerp(p0.halfW, p1.halfW, t)
            };
        }

        function riverSurfaceYAt(x) {
            return sampleRiverProfile(x).y;
        }

        function inRiverMask(x, z) {
            const p = sampleRiverProfile(x);
            return x >= 2.0 && x <= 138.0 && Math.abs(z - p.cz) <= p.halfW;
        }

        function createWaterMaterial(opts) {
            const o = opts || {};
            return new THREE.MeshStandardMaterial({
                color: o.color !== undefined ? o.color : 0x2d8fd6,
                transparent: true,
                opacity: o.opacity !== undefined ? o.opacity : 0.92,
                depthWrite: false,
                roughness: o.roughness !== undefined ? o.roughness : 0.08,
                metalness: o.metalness !== undefined ? o.metalness : 0.25,
                normalMap: waterNormalTex,
                normalScale: o.normalScale !== undefined ? o.normalScale : new THREE.Vector2(1.4, 1.4),
                emissive: new THREE.Color(0x0a2a3a),
                emissiveIntensity: o.emissiveIntensity !== undefined ? o.emissiveIntensity : 0.12,
                side: THREE.DoubleSide
            });
        }

        function addTerrain() {
            const sizeX = 260;
            const sizeZ = 180;
            const segX = 240;
            const segZ = 180;

            const geo = new THREE.PlaneGeometry(sizeX, sizeZ, segX, segZ);
            geo.rotateX(-Math.PI / 2);

            const pos = geo.attributes.position;
            const colors = [];

            for (let i = 0; i < pos.count; i++) {
                const x = pos.getX(i);
                const z = pos.getZ(i);
                const y = terrainHeight(x, z);
                pos.setY(i, y);

                let r = 0.72, g = 0.86, b = 0.62;
                if (y < 14) {
                    r = 0.83; g = 0.87; b = 0.70;
                } else if (y < 24) {
                    r = 0.70; g = 0.82; b = 0.58;
                } else if (y < 32) {
                    r = 0.58; g = 0.72; b = 0.49;
                } else {
                    r = 0.48; g = 0.61; b = 0.42;
                }

                colors.push(r, g, b);
            }

            geo.setAttribute("color", new THREE.Float32BufferAttribute(colors, 3));
            geo.setAttribute(
                "uv2",
                new THREE.Float32BufferAttribute(geo.attributes.uv.array.slice(), 2)
            );
            geo.computeVertexNormals();

            const mat = new THREE.MeshStandardMaterial({
                map: terrainDiffuseTex,
                roughnessMap: terrainArmTex,
                aoMap: terrainArmTex,
                metalnessMap: terrainArmTex,
                vertexColors: true,
                roughness: 0.95,
                metalness: 0.02
            });

            const mesh = new THREE.Mesh(geo, mat);
            staticGroup.add(mesh);
        }

        function addReservoirWater() {
            const points = [];
            const step = 4.0;

            for (let x = -128.0; x <= -4.0; x += step) {
                points.push(new THREE.Vector2(x, -reservoirHalfWidth(x) + 2.0));
            }
            for (let x = -4.0; x >= -128.0; x -= step) {
                points.push(new THREE.Vector2(x, reservoirHalfWidth(x) - 2.0));
            }

            const shape = new THREE.Shape(points);
            const geo = new THREE.ShapeGeometry(shape, 120);

            const pos = geo.attributes.position;
            for (let i = 0; i < pos.count; i++) {
                const x = pos.getX(i);
                const z = pos.getY(i);
                pos.setXYZ(i, x, state.waterLevel, z);
            }

            geo.computeVertexNormals();

            const mat = createWaterMaterial({
                color: 0x1a4f8f,          // ⭐和河道一致
                opacity: 0.90,            // ⭐更深一点
                roughness: 0.2,
                metalness: 0.05,
                normalScale: new THREE.Vector2(1.2, 1.2),
                emissiveIntensity: 0.15
            });

            const mesh = new THREE.Mesh(geo, mat);
            mesh.renderOrder = 1;   // ⭐关键：水后画
            dynamicGroup.add(mesh);
        }

        function addDamTransitionWater() {
            const geo = new THREE.PlaneGeometry(22, 28, 60, 30);
            geo.rotateX(-Math.PI / 2);

            const pos = geo.attributes.position;

            for (let i = 0; i < pos.count; i++) {
                const lx = pos.getX(i);
                const lz = pos.getZ(i);

                const x = lx - 6;
                const z = lz;

                const ground = terrainHeight(x, z);
                const t = clamp((x + 6) / 10.0, 0.0, 1.0);

                const upstreamY = state.waterLevel;
                const downstreamY = riverSurfaceYAt(2.0);

                let y = upstreamY * (1.0 - t) + downstreamY * t;
                y = Math.max(y, ground + 0.15);

                pos.setXYZ(i, x, y, z);
            }

            geo.computeVertexNormals();

            const mat = createWaterMaterial({
                color: 0x70c9ee,
                opacity: 0.76,
                roughness: 0.14,
                metalness: 0.05,
                normalScale: new THREE.Vector2(1.8, 1.8),
                emissiveIntensity: 0.07
            });

                const mesh = new THREE.Mesh(geo, mat);
                mesh.renderOrder = 1;   // ⭐关键：水后画
                dynamicGroup.add(mesh);
        }



        function addRiverWater() {
            const length = 136.0;
            const width = 34.0;
            const segX = 240;
            const segZ = 36;

            const geo = new THREE.PlaneGeometry(length, width, segX, segZ);
            geo.rotateX(-Math.PI / 2);

            const pos = geo.attributes.position;

            for (let i = 0; i < pos.count; i++) {
                const localX = pos.getX(i);
                const localZ = pos.getZ(i);

                const x = 2.0 + (localX + length * 0.5);
                const profile = sampleRiverProfile(x);

                const u = clamp(localZ / (width * 0.5), -1.0, 1.0);
                const finalZ = profile.cz + u * profile.halfW;

                const bankFade = Math.abs(u);
                let finalY = profile.y - Math.pow(bankFade, 1.5) * 0.15;

                const bed = terrainHeight(x, finalZ);
                const offset = 0.15 + state.qFactor * 0.1;
                finalY = Math.max(finalY, bed + offset);

                pos.setX(i, x);
                pos.setY(i, finalY);
                pos.setZ(i, finalZ);
            }

            geo.computeVertexNormals();

            const mat = createWaterMaterial({
                color: 0x1a4f8f,
                opacity: 0.90,
                emissive: new THREE.Color(0x0a1f3a),
                emissiveIntensity: 0.18,
                roughness: 0.2,
                metalness: 0.05,
                normalScale: new THREE.Vector2(1.8, 1.8),
                emissiveIntensity: 0.09
            });

                const mesh = new THREE.Mesh(geo, mat);
                mesh.renderOrder = 1;   // ⭐关键：水后画
                dynamicGroup.add(mesh);
        }

        function addShorelineTransitions() {
            const shoreMat = new THREE.MeshStandardMaterial({
                color: 0xcdbf98,
                roughness: 1.0,
                metalness: 0.0,
                transparent: true,
                opacity: 0.92,
                side: THREE.DoubleSide
            });

            const geo1 = new THREE.PlaneGeometry(150, 100, 180, 120);
            geo1.rotateX(-Math.PI / 2);
            const pos1 = geo1.attributes.position;

            for (let i = 0; i < pos1.count; i++) {
                const x = pos1.getX(i) - 48.0;
                const z = pos1.getZ(i);
                const bed = terrainHeight(x, z);
                const mask = inReservoirMask(x, z);

                if (mask && bed < state.waterLevel + 1.0 && bed > state.waterLevel - 1.8) {
                    pos1.setX(i, x);
                    pos1.setY(i, bed + 0.08);
                    pos1.setZ(i, z);
                } else {
                    pos1.setX(i, x);
                    pos1.setY(i, bed - 2.0);
                    pos1.setZ(i, z);
                }
            }

            geo1.computeVertexNormals();
            dynamicGroup.add(new THREE.Mesh(geo1, shoreMat));

            const geo2 = new THREE.PlaneGeometry(180, 42, 220, 40);
            geo2.rotateX(-Math.PI / 2);
            const pos2 = geo2.attributes.position;

            for (let i = 0; i < pos2.count; i++) {
                const x = pos2.getX(i) + 52.0;
                const localZ = pos2.getZ(i);

                const p = sampleRiverProfile(clamp(x, 2.0, 138.0));
                const z = p.cz + localZ;

                const bed = terrainHeight(x, z);
                const targetY = riverSurfaceYAt(clamp(x, 2.0, 138.0));

                if (inRiverMask(x, z) && bed < targetY + 0.9 && bed > targetY - 1.2) {
                    pos2.setX(i, x);
                    pos2.setY(i, bed + 0.07);
                    pos2.setZ(i, z);
                } else {
                    pos2.setX(i, x);
                    pos2.setY(i, bed - 2.0);
                    pos2.setZ(i, z);
                }
            }

            geo2.computeVertexNormals();
            dynamicGroup.add(new THREE.Mesh(geo2, shoreMat));
        }

        function addTreesNatural() {
            const group = new THREE.Group();
            staticGroup.add(group);

            const treeWaterLevel = state.waterLevel;

            function createTree(x, z) {
                const y = terrainHeight(x, z);
                if (y < treeWaterLevel + 1.5) return;

                const scale = 0.8 + Math.random() * 1.2;

                const trunk = new THREE.Mesh(
                    new THREE.CylinderGeometry(0.15 * scale, 0.2 * scale, 1.2 * scale, 6),
                    new THREE.MeshStandardMaterial({ color: 0x6b4f2a })
                );
                trunk.position.set(x, y + 0.6 * scale, z);

                const crown = new THREE.Mesh(
                    new THREE.ConeGeometry(0.9 * scale, 2.6 * scale, 8),
                    new THREE.MeshStandardMaterial({
                        color: new THREE.Color().setHSL(0.33 + Math.random() * 0.05, 0.6, 0.35)
                    })
                );
                crown.position.set(x, y + 2.0 * scale, z);

                group.add(trunk);
                group.add(crown);
            }

            for (let i = 0; i < 300; i++) {
                const x = -120 + Math.random() * 240;
                const z = -80 + Math.random() * 160;
                if (Math.abs(x) < 15 && Math.abs(z) < 25) continue;
                createTree(x, z);
            }
        }

        function addApron() {
            const apron = new THREE.Mesh(
                new THREE.BoxGeometry(18, 0.5, 16),
                new THREE.MeshStandardMaterial({
                    color: 0xd7dde3,
                    roughness: 0.88,
                    metalness: 0.02
                })
            );
            apron.position.set(6, terrainHeight(6, 0) + 0.25, 0);
            staticGroup.add(apron);
        }

        function loadDam() {
            try {
                const loader = new THREE.GLTFLoader();

                const binary = atob(GLB_BASE64);
                const array = new Uint8Array(binary.length);
                for (let i = 0; i < binary.length; i++) {
                    array[i] = binary.charCodeAt(i);
                }

                loader.parse(array.buffer, "", function (gltf) {
                    try {
                        const dam = gltf.scene;

                        const box0 = new THREE.Box3().setFromObject(dam);
                        const size0 = new THREE.Vector3();
                        box0.getSize(size0);

                        const targetHeight = 18.0;
                        const scale = targetHeight / Math.max(size0.y, 0.0001);
                        dam.scale.set(scale, scale, scale);

                        const box1 = new THREE.Box3().setFromObject(dam);
                        const center1 = new THREE.Vector3();
                        box1.getCenter(center1);

                        const baseY = terrainHeight(0.0, 0.0) - 0.8;

                        dam.position.set(
                            0.0 - center1.x,
                            baseY - box1.min.y,
                            0.0 - center1.z
                        );

                        dam.rotation.y = Math.PI / 2.0;
                        dam.renderOrder = 0;
                        staticGroup.add(dam);
                    } catch (e) {
                        showError("坝体解析后处理失败: " + e);
                    }
                }, function (err) {
                    showError("GLB 解析失败: " + err);
                });
            } catch (e) {
                showError("GLB 加载失败: " + e);
            }
        }

        function disposeMaterial(mat) {
            if (!mat) return;
            if (Array.isArray(mat)) {
                for (let i = 0; i < mat.length; i++) {
                    if (mat[i] && mat[i].dispose) mat[i].dispose();
                }
            } else if (mat.dispose) {
                mat.dispose();
            }
        }

        function disposeNode(node) {
            if (!node) return;
            if (node.geometry) node.geometry.dispose();
            if (node.material) disposeMaterial(node.material);
        }

        function clearDynamicGroup() {
            for (let i = dynamicGroup.children.length - 1; i >= 0; i--) {
                const child = dynamicGroup.children[i];
                dynamicGroup.remove(child);
                child.traverse(function (obj) {
                    disposeNode(obj);
                });
            }
        }

        function rebuildDynamicScene() {
            waterNormalTex.repeat.set(state.rippleRepeat, state.rippleRepeat);
            buildRiverProfile();
            addShorelineTransitions();
            addReservoirWater();
            addDamTransitionWater();
            addRiverWater();
        }

        function setDispatchHour(hour) {
            state = getStateByHour(hour);
            clearDynamicGroup();
            rebuildDynamicScene();
            updateInfoPanel();
        }

        function onResize() {
            const w = Math.max(1, container.clientWidth || window.innerWidth);
            const h = Math.max(1, container.clientHeight || window.innerHeight);
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            renderer.setSize(w, h);
        }

        addTerrain();
        addApron();
        addTreesNatural();
        loadDam();
        rebuildDynamicScene();
        updateInfoPanel();

        window.setDispatchHour = setDispatchHour;
        window.addEventListener("resize", onResize);

        function animate() {
            requestAnimationFrame(animate);

            waterNormalTex.offset.x += state.flowOffsetX;
            waterNormalTex.offset.y += state.flowOffsetY;

            controls.update();
            renderer.render(scene, camera);
        }

        onResize();
        animate();

    } catch (e) {
        showError("主脚本错误: " + e.stack || e);
    }

})();
</script>
</body>
</html>
"""
    return html


def line_chart(hours, y, title, yname):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=y, mode="lines+markers",
        line=dict(width=3, color="#1f77d0"), marker=dict(size=6, color="#1f77d0")
    ))
    return apply_clean_layout(fig, title, "小时", yname, height=270)


def multi_line_chart(hours, series_dict, title, yname):
    fig = go.Figure()
    for name, y in series_dict.items():
        fig.add_trace(go.Scatter(
            x=hours, y=y, mode="lines+markers", name=name,
            line=dict(width=2), marker=dict(size=5)
        ))
    return apply_clean_layout(fig, title, "小时", yname, height=300)


def compare_bar(results):
    names = list(results.keys())
    revenues = [results[k]["detail"]["revenue"] for k in names]
    objectives = [results[k]["detail"]["objective"] for k in names]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=names, y=revenues, name="收益"))
    fig.add_trace(go.Bar(x=names, y=objectives, name="综合目标"))
    fig.update_layout(barmode="group")
    return apply_clean_layout(fig, "不同调度策略对比", "方法", "指标值", height=320)


def get_recommendation(results):
    best_name = max(results, key=lambda k: results[k]["detail"]["objective"])
    d = results[best_name]["detail"]
    reason = f"{best_name} 的综合目标函数最高（{d['objective']:.0f}），且兼顾收益与平稳性。"
    return best_name, reason


def build_alerts(detail, params, hour):
    msgs = []
    s = detail["S"][hour]
    if s > params["S_max"] * 0.95:
        msgs.append("当前库容接近上限，需关注弃水风险。")
    if s < params["S_min"] * 1.10:
        msgs.append("当前库容接近下限，需关注后续调度裕度。")
    if detail["spill"] > 0:
        msgs.append("本方案存在弃水现象，可进一步优化泄流策略。")
    if detail["smooth_penalty"] > 2200:
        msgs.append("出力波动偏大，建议优先考虑平稳性更好的策略。")
    if not msgs:
        msgs.append("当前运行状态正常，调度方案满足主要约束条件。")
    return msgs


def build_result_table(results):
    rows = []
    for name, result in results.items():
        d = result["detail"]
        rows.append({
            "策略": name,
            "总收益(元)": round(d["revenue"], 2),
            "综合目标": round(d["objective"], 2),
            "平滑指标": round(d["smooth_penalty"], 2),
            "弃水量": round(d["spill"], 4),
            "末时段库容": round(d["S"][-1], 2),
            "平均出力(MW)": round(float(np.mean(d["power_mw"])), 2),
        })
    return pd.DataFrame(rows)


# =========================================================
# 4. 计算所有方案
# =========================================================
@st.cache_data
def run_all_methods(seed, beta_smooth, s0, smin, smax, qmin, qmax, head, eta):
    inflow, price = make_synthetic_inputs(seed=seed)
    params = dict(
        S0=s0,
        S_min=smin,
        S_max=smax,
        Q_min=qmin,
        Q_max=qmax,
        head=head,
        eta=eta,
        alpha_spill=2.0,
        beta_smooth=beta_smooth,
        k_storage=3600.0 / 2e5,
        penalty_big=1e9,
    )

    results = {}

    Q_rule = rule_based_schedule(inflow, price, params)
    _, d_rule = simulate_schedule(Q_rule, inflow, price, params)
    results["Rule"] = {"Q": Q_rule, "detail": d_rule, "history": None}

    Q_pso, _, hist_pso = pso_optimize(inflow, price, params)
    _, d_pso = simulate_schedule(Q_pso, inflow, price, params)
    results["PSO"] = {"Q": Q_pso, "detail": d_pso, "history": hist_pso}

    Q_apso, _, hist_apso = apso_ls_optimize(inflow, price, params)
    _, d_apso = simulate_schedule(Q_apso, inflow, price, params)
    results["APSO-LS"] = {"Q": Q_apso, "detail": d_apso, "history": hist_apso}

    Q_ga, _, hist_ga = ga_optimize(inflow, price, params)
    _, d_ga = simulate_schedule(Q_ga, inflow, price, params)
    results["GA"] = {"Q": Q_ga, "detail": d_ga, "history": hist_ga}

    return inflow, price, params, results


# =========================================================
# 5. 侧边栏
# =========================================================
with st.sidebar:
    st.header("系统配置")
    seed = st.number_input("随机种子", min_value=1, max_value=9999, value=42, step=1)
    beta_smooth = st.slider("平滑权重 β", min_value=0.0, max_value=10.0, value=5.0, step=0.5)

    st.header("水库参数")
    s0 = st.slider("初始库容 S0", 20.0, 60.0, 50.0, 1.0)
    smin = st.slider("最小库容 S_min", 10.0, 30.0, 20.0, 1.0)
    smax = st.slider("最大库容 S_max", 40.0, 80.0, 55.0, 1.0)
    qmin = st.slider("最小下泄 Q_min", 10.0, 80.0, 30.0, 1.0)
    qmax = st.slider("最大下泄 Q_max", 100.0, 300.0, 220.0, 5.0)
    head = st.slider("有效水头 H", 20.0, 120.0, 50.0, 1.0)
    eta = st.slider("机组效率 η", 0.70, 0.98, 0.90, 0.01)

    st.header("展示模式")

    scene_mode = st.radio(
        "场景模式",
        ["2D场景", "3D场景", "2D+3D对照"]
    )

    page_mode = st.radio(
        "页面模式",
        ["单策略分析", "多策略对比"]
    )

    algo = st.selectbox(
        "当前策略",
        ["Rule", "PSO", "APSO-LS", "GA"]
    )

    st.markdown("### 🎬 演示模式")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶ 一键演示"):
            st.session_state.demo_mode = True
            st.session_state.demo_hour = 0
            st.session_state.demo_strategy_idx = 0

    with col2:
        if st.button("⏹ 停止"):
            st.session_state.demo_mode = False

    auto_play = st.checkbox("自动播放 24h", value=False)

    if scene_mode != "2D场景" and auto_play:
        st.warning("3D场景不建议自动播放，建议使用 2D 场景或关闭自动播放。")

    if not auto_play:
        hour = st.slider("当前时刻", 0, 23, 16, 1)
    else:
        hour = 0

# =========================================================
# 6. 主界面
# =========================================================
inject_dashboard_css()

inflow, price, params, results = run_all_methods(
    seed, beta_smooth, s0, smin, smax, qmin, qmax, head, eta
)
selected = results[algo]
Q = selected["Q"]
detail = selected["detail"]
hours = np.arange(24)
best_name, best_reason = get_recommendation(results)
table_data = build_result_table(results)

display_name = "APSO-LS" if best_name == "APSO-LS" else best_name

st.markdown("""
<div class="dashboard-title">
    <h1>水电站智能调度可视化监控大屏</h1>
    <p>Hydropower Intelligent Dispatch Visualization Center · 稳定版工程升级 </p>
    <div class="status-chip-wrap">
        <div class="status-chip">运行模式：日内优化调度</div>
        <div class="status-chip">三维引擎：Three.js Embedded</div>
        <div class="status-chip">求解核心：PSO / GA / APSO-LS</div>
        <div class="status-chip">数据链路：Python → JS 驱动</div>
    </div>
</div>
""", unsafe_allow_html=True)

top1, top2, top3, top4, top5 = st.columns(5)
top1.metric("推荐策略", display_name)
top2.metric("当前策略", algo)
top3.metric("当前策略收益", f"{detail['revenue']:.0f} 元")
top4.metric("综合目标", f"{detail['objective']:.0f}")
top5.metric("当前时刻", f"{(hour if not auto_play else 0):02d}:00")

st.success(f"系统推荐：{best_name}。{best_reason}")

with st.expander("系统说明", expanded=False):
    st.write(
        "本系统集成入流与电价数据输入、多目标优化求解、调度策略对比、运行状态展示与三维可视化仿真功能。"
        "当前版本在现有稳定系统基础上进行工程级升级，本步骤仅优化整体页面结构与大屏视觉布局，不改变算法与数据驱动主链路。"
    )

alerts = build_alerts(detail, params, hour if not auto_play else 0)
for msg in alerts:
    st.info(msg)


def render_dashboard_main(hour, strategy_override=None):
    current_algo = strategy_override if strategy_override is not None else algo
    current_result = results[current_algo]
    current_Q = current_result["Q"]
    current_detail = current_result["detail"]

    left_col, center_col, right_col = st.columns([1.15, 2.9, 1.15], gap="medium")

    with left_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">运行态势</div>', unsafe_allow_html=True)

        m1, m2 = st.columns(2)
        with m1:
            st.metric("时刻", f"{hour:02d}:00")
        with m2:
            mode_text = "演示" if st.session_state.demo_mode else ("自动" if auto_play else "手动")
            st.metric("模式", mode_text)

        st.metric("入流量", f"{inflow[hour]:.2f} m³/s")
        st.metric("下泄流量", f"{current_Q[hour]:.2f} m³/s")
        st.metric("机组出力", f"{current_detail['power_mw'][hour]:.2f} MW")
        st.metric("当前库容", f"{current_detail['S'][hour]:.2f}")
        st.metric("累计收益", f"{current_detail['cum_revenue'][hour]:.0f} 元")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">调度策略信息</div>', unsafe_allow_html=True)
        st.write(f"**当前策略：** {current_algo}")
        st.write(f"**推荐策略：** {best_name}")
        st.write(f"**平滑权重 β：** {beta_smooth:.1f}")
        st.write(f"**场景模式：** {scene_mode}")
        st.write(f"**页面模式：** {page_mode}")
        st.markdown('</div>', unsafe_allow_html=True)

    with center_col:
        st.markdown("""
        <div class="main-3d-wrap">
            <div class="main-3d-title">
                <div class="main-3d-title-left">三维调度场景主视图</div>
                <div class="main-3d-title-right">3D视觉中心 / Reservoir-Dam-River Scene</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if scene_mode == "2D场景":
            fig_2d = build_reservoir_scene_2d(
                storage=current_detail["S"][hour],
                params=params,
                release=current_Q[hour],
                inflow=inflow[hour],
                power=current_detail["power_mw"][hour],
                hour=hour
            )
            fig_2d.update_layout(
                height=620,
                paper_bgcolor="rgba(255,255,255,0.0)",
                plot_bgcolor="rgba(240,248,255,0.98)"
            )
            st.plotly_chart(fig_2d, width="stretch", config={"displayModeBar": False})

        elif scene_mode == "3D场景":
            html = build_threejs_html(
                detail=current_detail,
                Q=current_Q,
                inflow=inflow,
                hour=hour,
                auto_play=auto_play
            )
            components.html(html, height=620)

        else:
            dual1, dual2 = st.columns([1, 1], gap="small")
            with dual1:
                fig_2d = build_reservoir_scene_2d(
                    storage=current_detail["S"][hour],
                    params=params,
                    release=current_Q[hour],
                    inflow=inflow[hour],
                    power=current_detail["power_mw"][hour],
                    hour=hour
                )
                fig_2d.update_layout(
                    height=620,
                    paper_bgcolor="rgba(255,255,255,0.0)",
                    plot_bgcolor="rgba(240,248,255,0.98)"
                )
                st.plotly_chart(fig_2d, width="stretch", config={"displayModeBar": False})

            with dual2:
                html = build_threejs_html(
                    detail=current_detail,
                    Q=current_Q,
                    inflow=inflow,
                    hour=hour,
                    auto_play=auto_play
                )
                components.html(html, height=620)

        st.markdown('<div class="chart-panel">', unsafe_allow_html=True)
        trend1, trend2 = st.columns(2)

        with trend1:
            st.plotly_chart(
                line_chart(hours, current_Q, f"{current_algo} 调度出流曲线", "出流(m³/s)"),
                width="stretch"
            )

        with trend2:
            st.plotly_chart(
                line_chart(np.arange(25), current_detail["S"], f"{current_algo} 库容变化曲线", "库容"),
                width="stretch"
            )

        st.markdown('</div>', unsafe_allow_html=True)

    with right_col:

        st.metric("总收益", f"{current_detail['revenue']:.0f} 元")
        st.metric("平滑指标", f"{current_detail['smooth_penalty']:.2f}")
        st.metric("弃水量", f"{current_detail['spill']:.4f}")
        st.metric("综合目标", f"{current_detail['objective']:.0f}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">外部环境输入</div>', unsafe_allow_html=True)
        st.metric("当前电价", f"{price[hour]:.2f}")
        st.metric("24h平均入流", f"{np.mean(inflow):.2f} m³/s")
        st.metric("24h平均电价", f"{np.mean(price):.2f}")
        st.metric("最大出流约束", f"{params['Q_max']:.1f} m³/s")
        st.markdown('</div>', unsafe_allow_html=True)


strategies = ["Rule", "PSO", "APSO-LS"]

if st.session_state.demo_mode:
    demo_strategy = strategies[st.session_state.demo_strategy_idx]
    demo_hour = st.session_state.demo_hour

    render_dashboard_main(demo_hour, strategy_override=demo_strategy)

    st.session_state.demo_hour += 1
    if st.session_state.demo_hour >= 24:
        st.session_state.demo_hour = 0
        st.session_state.demo_strategy_idx = (
                                                     st.session_state.demo_strategy_idx + 1
                                             ) % len(strategies)

    time.sleep(0.6)
    st.rerun()

if page_mode == "单策略分析":
    if auto_play and scene_mode == "2D场景":
        t = st.session_state.play_hour
        render_dashboard_main(t)
        st.session_state.play_hour = (t + 1) % 24
        time.sleep(0.5)
        st.rerun()
    else:
        st.session_state.play_hour = hour  # ⭐关键
        render_dashboard_main(hour)

    st.markdown("---")

    row_a1, row_a2 = st.columns(2)
    with row_a1:
        st.plotly_chart(
            line_chart(hours, inflow, "24小时入流曲线", "入流(m³/s)"),
            width="stretch"
        )
    with row_a2:
        st.plotly_chart(
            line_chart(hours, price, "24小时电价曲线", "电价"),
            width="stretch"
        )

    row_b1, row_b2 = st.columns(2)
    with row_b1:
        st.plotly_chart(
            line_chart(hours, detail["power_mw"], f"{algo} 出力曲线", "功率(MW)"),
            width="stretch"
        )
    with row_b2:
        st.plotly_chart(
            line_chart(hours, detail["cum_revenue"], f"{algo} 累计收益曲线", "累计收益(元)"),
            width="stretch"
        )

    hist = results[algo]["history"]
    if hist is not None:
        st.plotly_chart(
            line_chart(np.arange(len(hist)), hist, f"{algo} 收敛过程", "目标函数"),
            width="stretch"
        )

else:
    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">多策略运行对比总览</div>', unsafe_allow_html=True)

    cc1, cc2, cc3, cc4 = st.columns(4)
    for col, name in zip([cc1, cc2, cc3, cc4], results.keys()):
        d = results[name]["detail"]
        col.metric(
            name,
            f"{d['revenue']:.0f} 元",
            delta=f"Obj={d['objective']:.0f}"
        )

    st.markdown('</div>', unsafe_allow_html=True)

    st.plotly_chart(
        multi_line_chart(
            hours,
            {k: results[k]["Q"] for k in results.keys()},
            "不同策略出流曲线对比",
            "出流(m³/s)"
        ),
        width="stretch"
    )

    compare_c1, compare_c2 = st.columns(2)
    with compare_c1:
        st.plotly_chart(
            multi_line_chart(
                np.arange(25),
                {k: results[k]["detail"]["S"] for k in results.keys()},
                "不同策略库容变化对比",
                "库容"
            ),
            width="stretch"
        )
    with compare_c2:
        st.plotly_chart(
            multi_line_chart(
                hours,
                {k: results[k]["detail"]["power_mw"] for k in results.keys()},
                "不同策略出力曲线对比",
                "功率(MW)"
            ),
            width="stretch"
        )

    st.plotly_chart(compare_bar(results), width="stretch")

st.markdown('<div class="panel-card">', unsafe_allow_html=True)
st.markdown('<div class="panel-title">调度结果评价表</div>', unsafe_allow_html=True)
st.dataframe(table_data, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

csv_bytes = table_data.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "下载评价表 CSV",
    data=csv_bytes,
    file_name="hydro_dispatch_results.csv",
    mime="text/csv"
)
