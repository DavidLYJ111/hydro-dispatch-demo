import time
import json
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

# ===== Session 初始化（必须在最前）=====
if "play_hour" not in st.session_state:
    st.session_state.play_hour = 0

if "demo_mode" not in st.session_state:
    st.session_state.demo_mode = False

if "demo_hour" not in st.session_state:
    st.session_state.demo_hour = 0

if "demo_strategy_idx" not in st.session_state:
    st.session_state.demo_strategy_idx = 0

if "demo_speed" not in st.session_state:
    st.session_state.demo_speed = 1.0

st.set_page_config(page_title="智调水电Demo", layout="wide")


def inject_dashboard_css():

    st.markdown("""
    <style>
    .stApp {
        background: #F5F7FA;
        color: #1F2937;
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
        background: linear-gradient(135deg, #e6f4ff 0%, #f0f9ff 100%);
        border: 1px solid #c7e0ff;
        padding: 20px 24px;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    
    .dashboard-title h1 {
        color: #111827;
    }
    
    .dashboard-title p {
        color: #6B7280;
    }

    .panel-card {
        background: #f4f9ff;
        border: 1px solid #dbeafe;
    }

    .panel-title {
        font-size: 15px;
        font-weight: 800;
        color: #111827;
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
        background: rgba(34, 211, 238, 0.12);
        border: 1px solid rgba(34, 211, 238, 0.32);
        color: #d7f6ff;
        font-size: 12px;
        font-weight: 600;
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(180deg, rgba(9, 35, 63, 0.62), rgba(8, 24, 44, 0.58));
        border: 1px solid rgba(34, 211, 238, 0.22);
        border-radius: 16px;
        padding: 10px 12px;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.04), 0 10px 22px rgba(0,0,0,0.30);
        backdrop-filter: blur(6px);
    }

    div[data-testid="metric-container"] label {
        color: #8ec6ef !important;
        font-weight: 600;
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #e4f4ff !important;
    }

    .main-3d-wrap {
        background: #FFFFFF;
        border: 1px solid #E5EAF0;
        border-radius: 16px;
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
        color: #c7f2ff;
        letter-spacing: 0.3px;
    }

    .main-3d-title-right {
        font-size: 12px;
        color: #95d9ff;
        background: rgba(10, 132, 255, 0.15);
        border: 1px solid rgba(34, 211, 238, 0.24);
        border-radius: 999px;
        padding: 5px 10px;
    }

    .chart-panel {
        background: #FFFFFF;
        border: 1px solid #E5EAF0;
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
        border: 1px solid rgba(34, 211, 238, 0.22);
        box-shadow: 0 10px 24px rgba(0, 10, 26, 0.36);
        background: #ffffff;
    }

    .kpi-best {
        border: 1px solid rgba(255, 209, 102, 0.55);
        border-radius: 12px;
        background: linear-gradient(180deg, rgba(255, 209, 102, 0.18), rgba(255, 209, 102, 0.08));
        color: #ffeab5;
        padding: 8px 12px;
        margin-top: 6px;
        font-size: 13px;
        font-weight: 700;
        box-shadow: 0 6px 16px rgba(255, 209, 102, 0.18);
    }

    .demo-running {
        margin-top: 8px;
        margin-bottom: 6px;
        display: inline-block;
        border-radius: 999px;
        background: rgba(34, 197, 94, 0.22);
        border: 1px solid rgba(74, 222, 128, 0.55);
        color: #bbf7d0;
        font-weight: 700;
        padding: 6px 12px;
        font-size: 12px;
    }

    .analysis-title {
        color: #bcecff;
        font-size: 16px;
        font-weight: 800;
        margin-top: 14px;
        margin-bottom: 6px;
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
    import numpy as np
    import plotly.graph_objects as go

    if "action" in st.session_state:
        if st.session_state["action"] == "increase_release":
            release *= 1.2
    # =========================
    # 1) 数据归一化（不改算法，只做显示映射）
    # =========================
    s_min = float(params["S_min"])
    s_max = float(params["S_max"])
    q_min = float(params["Q_min"])
    q_max = float(params["Q_max"])

    storage_ratio = (float(storage) - s_min) / (s_max - s_min + 1e-9)
    storage_ratio = float(np.clip(storage_ratio, 0.0, 1.0))

    release_ratio = (float(release) - q_min) / (q_max - q_min + 1e-9)
    inflow_ratio = (float(inflow) - q_min) / (q_max - q_min + 1e-9)
    release_ratio = float(np.clip(release_ratio, 0.0, 1.0))
    inflow_ratio = float(np.clip(inflow_ratio, 0.0, 1.0))

    # 水位高度（工业示意映射）
    water_y = 28 + 26 * storage_ratio

    # 下泄主通道厚度 / 入流箭头粗细
    release_thickness = 4.0 + 10.0 * release_ratio
    inflow_arrow_width = 2.0 + 7.0 * inflow_ratio

    # 发电强度仅用于视觉亮度，不影响逻辑
    power_ratio = float(np.clip(power / 120.0, 0.0, 1.0))

    # =========================
    # 2) 统一工业白底科研风配色
    # =========================
    c_bg = "#F7FAFC"
    c_panel = "#FFFFFF"
    c_panel_border = "#D9E2EC"

    c_mountain = "#D6DEE6"
    c_terrain = "#E8EEF4"
    c_dam_main = "#AAB4C0"
    c_dam_edge = "#6B7785"
    c_gate = "#7D8B99"
    c_water = "#4DA3D9"
    c_water_deep = "#2E7FB7"
    c_water_light = "#BFE6FA"
    c_flow = "#1683C7"
    c_flow_soft = "rgba(22,131,199,0.18)"
    c_inflow = "#23A36D"
    c_power = "#F59E0B"
    c_text = "#243746"
    c_subtext = "#61758A"
    c_grid = "rgba(80,110,140,0.10)"

    fig = go.Figure()

    # =========================
    # 3) 背景分层（工业面板感）
    # =========================
    # 外框底板
    fig.add_shape(
        type="rect", x0=0, x1=100, y0=0, y1=70,
        line=dict(color="#E4EBF2", width=1),
        fillcolor=c_bg,
        layer="below"
    )

    # 上部结构区域
    fig.add_shape(
        type="rect", x0=0, x1=100, y0=8, y1=66,
        line=dict(color="rgba(0,0,0,0)", width=0),
        fillcolor="#FBFDFF",
        layer="below"
    )

    # 下部信息带
    fig.add_shape(
        type="rect", x0=0, x1=100, y0=0, y1=8,
        line=dict(color="#E4EBF2", width=1),
        fillcolor="#F3F7FA",
        layer="below"
    )

    # 轻网格线
    for xg in np.linspace(8, 92, 8):
        fig.add_shape(
            type="line", x0=xg, x1=xg, y0=10, y1=64,
            line=dict(color=c_grid, width=1),
            layer="below"
        )
    for yg in [18, 28, 38, 48, 58]:
        fig.add_shape(
            type="line", x0=6, x1=94, y0=yg, y1=yg,
            line=dict(color=c_grid, width=1),
            layer="below"
        )

    # =========================
    # 4) 山体 / 地形轮廓（更偏平台工业风）
    # =========================
    terrain_x = [0, 8, 16, 25, 35, 48, 58, 68, 78, 88, 100, 100, 0]
    terrain_y = [60, 63, 58, 64, 57, 62, 56, 61, 58, 63, 60, 8, 8]
    fig.add_trace(go.Scatter(
        x=terrain_x, y=terrain_y,
        fill="toself",
        mode="lines",
        line=dict(color="#C7D1DB", width=1.5),
        fillcolor=c_terrain,
        hoverinfo="skip",
        showlegend=False
    ))

    # 远景浅层
    terrain2_x = [0, 12, 24, 37, 50, 65, 80, 100, 100, 0]
    terrain2_y = [54, 57, 53, 58, 54, 57, 55, 58, 48, 48]
    fig.add_trace(go.Scatter(
        x=terrain2_x, y=terrain2_y,
        fill="toself",
        mode="lines",
        line=dict(color="rgba(0,0,0,0)", width=0),
        fillcolor="rgba(214,222,230,0.55)",
        hoverinfo="skip",
        showlegend=False
    ))

    # =========================
    # 5) 水库水体（动态水位）
    # =========================
    water_poly_x = [14, 20, 61, 66, 66, 14]
    water_poly_y = [14, water_y, water_y, water_y - 2.8, 14, 14]

    fig.add_trace(go.Scatter(
        x=water_poly_x, y=water_poly_y,
        fill="toself",
        mode="lines",
        line=dict(color=c_water_deep, width=2),
        fillcolor="rgba(77,163,217,0.78)",
        hoverinfo="skip",
        showlegend=False
    ))

    # 水体高光层
    fig.add_trace(go.Scatter(
        x=[19, 60, 63, 22],
        y=[water_y - 0.8, water_y - 0.8, water_y - 2.0, water_y - 2.0],
        fill="toself",
        mode="lines",
        line=dict(color="rgba(0,0,0,0)", width=0),
        fillcolor="rgba(255,255,255,0.18)",
        hoverinfo="skip",
        showlegend=False
    ))

    # 水位线
    fig.add_trace(go.Scatter(
        x=[18, 64],
        y=[water_y, water_y],
        mode="lines",
        line=dict(color="#1E6FAE", width=2.2, dash="dash"),
        hoverinfo="skip",
        showlegend=False
    ))

    # 水位刻度尺
    fig.add_shape(
        type="line", x0=12.2, x1=12.2, y0=14, y1=56,
        line=dict(color="#90A4B8", width=2)
    )
    for yt in [18, 26, 34, 42, 50]:
        fig.add_shape(
            type="line", x0=11.2, x1=12.8, y0=yt, y1=yt,
            line=dict(color="#90A4B8", width=1.2)
        )

    # =========================
    # 6) 坝体 / 闸门 / 厂房（工业化几何）
    # =========================
    # 坝体主块
    dam_x = [61, 68, 70, 66, 61]
    dam_y = [14, 14, 56, 56, 14]
    fig.add_trace(go.Scatter(
        x=dam_x, y=dam_y,
        fill="toself",
        mode="lines",
        line=dict(color=c_dam_edge, width=2.5),
        fillcolor=c_dam_main,
        hoverinfo="skip",
        showlegend=False
    ))

    # 坝体阴影立面
    fig.add_trace(go.Scatter(
        x=[68, 71.2, 73.2, 70, 68],
        y=[14, 14.6, 56.8, 56, 14],
        fill="toself",
        mode="lines",
        line=dict(color="#7B8794", width=1.5),
        fillcolor="rgba(125,139,153,0.78)",
        hoverinfo="skip",
        showlegend=False
    ))

    # 闸门结构
    gate_x = [67.8, 69.0, 69.0, 67.8, 67.8]
    gate_y = [28, 28, 44, 44, 28]
    fig.add_trace(go.Scatter(
        x=gate_x, y=gate_y,
        fill="toself",
        mode="lines",
        line=dict(color="#5E6C79", width=1.5),
        fillcolor=c_gate,
        hoverinfo="skip",
        showlegend=False
    ))

    # 厂房
    plant_x = [56.5, 61, 61, 56.5, 56.5]
    plant_y = [12.2, 12.2, 18.2, 18.2, 12.2]
    fig.add_trace(go.Scatter(
        x=plant_x, y=plant_y,
        fill="toself",
        mode="lines",
        line=dict(color="#8C6A3A", width=1.5),
        fillcolor="#C9A46D",
        hoverinfo="skip",
        showlegend=False
    ))

    # 厂房发电高亮
    fig.add_shape(
        type="rect",
        x0=57.0, x1=60.5, y0=13.0, y1=17.4,
        line=dict(color="rgba(0,0,0,0)", width=0),
        fillcolor=f"rgba(245,158,11,{0.15 + 0.35 * power_ratio})"
    )

    # =========================
    # 7) 入流动态（箭头+流线）
    # =========================
    # 入流主管线
    fig.add_trace(go.Scatter(
        x=[3, 10.5, 15.0],
        y=[water_y + 3.5, water_y + 2.0, water_y + 1.0],
        mode="lines",
        line=dict(color=c_inflow, width=inflow_arrow_width),
        hoverinfo="skip",
        showlegend=False
    ))

    # 入流箭头
    fig.add_annotation(
        x=15.0, y=water_y + 1.0,
        ax=7.2, ay=water_y + 2.7,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.2,
        arrowwidth=max(1.6, inflow_arrow_width * 0.75),
        arrowcolor=c_inflow
    )

    # 入流水纹辅助
    for dx in [0.0, 1.6, 3.2]:
        fig.add_trace(go.Scatter(
            x=[2.0 + dx, 5.5 + dx, 9.0 + dx],
            y=[water_y + 6.2, water_y + 5.5, water_y + 4.8],
            mode="lines",
            line=dict(color="rgba(35,163,109,0.18)", width=1.4),
            hoverinfo="skip",
            showlegend=False
        ))

    # =========================
    # 8) 下泄动态（宽度 / 多条流线 / 箭头）
    # =========================
    # 主泄流带
    fig.add_trace(go.Scatter(
        x=[69.0, 75.0, 83.0, 92.0],
        y=[36.0, 34.5, 31.8, 30.0],
        mode="lines",
        line=dict(color=c_flow, width=release_thickness),
        hoverinfo="skip",
        showlegend=False
    ))

    # 上下两条辅助流线，形成“流量宽度感”
    aux_offset = 0.8 + 2.2 * release_ratio
    fig.add_trace(go.Scatter(
        x=[69.0, 75.0, 83.0, 92.0],
        y=[36.0 + aux_offset, 34.5 + aux_offset, 31.8 + aux_offset, 30.0 + aux_offset],
        mode="lines",
        line=dict(color=c_flow_soft, width=max(1.2, release_thickness * 0.36)),
        hoverinfo="skip",
        showlegend=False
    ))
    fig.add_trace(go.Scatter(
        x=[69.0, 75.0, 83.0, 92.0],
        y=[36.0 - aux_offset, 34.5 - aux_offset, 31.8 - aux_offset, 30.0 - aux_offset],
        mode="lines",
        line=dict(color=c_flow_soft, width=max(1.2, release_thickness * 0.36)),
        hoverinfo="skip",
        showlegend=False
    ))

    # 末端箭头
    fig.add_annotation(
        x=92.0, y=30.0,
        ax=84.5, ay=31.8,
        xref="x", yref="y", axref="x", ayref="y",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.25,
        arrowwidth=max(2.0, release_thickness * 0.62),
        arrowcolor=c_flow
    )

    # =========================
    # 9) 库容变化条 / 流量条 / 功率条（面板式工业信息）
    # =========================
    # 右上信息面板背景
    fig.add_shape(
        type="rect", x0=74.5, x1=98, y0=48.5, y1=64.5,
        line=dict(color=c_panel_border, width=1),
        fillcolor=c_panel
    )

    # 库容条
    fig.add_shape(
        type="rect", x0=77, x1=95, y0=59.0, y1=61.2,
        line=dict(color="#D9E2EC", width=1),
        fillcolor="#EEF3F7"
    )
    fig.add_shape(
        type="rect", x0=77, x1=77 + 18 * storage_ratio, y0=59.0, y1=61.2,
        line=dict(color="rgba(0,0,0,0)", width=0),
        fillcolor=c_water
    )

    # 下泄条
    fig.add_shape(
        type="rect", x0=77, x1=95, y0=55.2, y1=57.4,
        line=dict(color="#D9E2EC", width=1),
        fillcolor="#EEF3F7"
    )
    fig.add_shape(
        type="rect", x0=77, x1=77 + 18 * release_ratio, y0=55.2, y1=57.4,
        line=dict(color="rgba(0,0,0,0)", width=0),
        fillcolor=c_flow
    )

    # 功率条
    fig.add_shape(
        type="rect", x0=77, x1=95, y0=51.4, y1=53.6,
        line=dict(color="#D9E2EC", width=1),
        fillcolor="#EEF3F7"
    )
    fig.add_shape(
        type="rect", x0=77, x1=77 + 18 * power_ratio, y0=51.4, y1=53.6,
        line=dict(color="rgba(0,0,0,0)", width=0),
        fillcolor=c_power
    )

    # =========================
    # 10) 文本标注（统一科研平台风）
    # =========================
    fig.add_annotation(
        x=7.5, y=62.5,
        text="<b>Hydro Dispatch 2D Synoptic View</b>",
        showarrow=False,
        font=dict(size=16, color=c_text),
        xanchor="left"
    )

    fig.add_annotation(
        x=7.5, y=59.4,
        text=f"Hour {int(hour):02d}:00  |  工业二维运行示意",
        showarrow=False,
        font=dict(size=10.5, color=c_subtext),
        xanchor="left"
    )

    fig.add_annotation(
        x=38, y=water_y + 2.8,
        text=f"坝前水位 {storage_ratio * 100:.1f}%",
        showarrow=False,
        font=dict(size=11, color="#1E6FAE"),
        bgcolor="rgba(255,255,255,0.82)",
        bordercolor="rgba(30,111,174,0.18)",
        borderwidth=1
    )

    fig.add_annotation(
        x=10.5, y=water_y + 8.0,
        text=f"入流 {float(inflow):.1f} m³/s",
        showarrow=False,
        font=dict(size=10.5, color=c_inflow),
        bgcolor="rgba(255,255,255,0.78)",
        bordercolor="rgba(35,163,109,0.15)",
        borderwidth=1
    )

    fig.add_annotation(
        x=84.5, y=26.2,
        text=f"下泄 {float(release):.1f} m³/s",
        showarrow=False,
        font=dict(size=10.5, color=c_flow),
        bgcolor="rgba(255,255,255,0.80)",
        bordercolor="rgba(22,131,199,0.18)",
        borderwidth=1
    )

    fig.add_annotation(
        x=58.6, y=19.8,
        text="厂房",
        showarrow=False,
        font=dict(size=10.5, color="#8C6A3A"),
        bgcolor="rgba(255,255,255,0.76)"
    )

    fig.add_annotation(
        x=66.0, y=58.8,
        text="坝体",
        showarrow=False,
        font=dict(size=10.5, color=c_dam_edge),
        bgcolor="rgba(255,255,255,0.76)"
    )

    fig.add_annotation(
        x=68.4, y=46.0,
        text="闸门",
        showarrow=False,
        font=dict(size=10.2, color="#5E6C79"),
        bgcolor="rgba(255,255,255,0.76)"
    )

    # 右上统计文字
    fig.add_annotation(
        x=76.2, y=62.5,
        text="<b>运行指标</b>",
        showarrow=False,
        xanchor="left",
        font=dict(size=11.5, color=c_text)
    )
    fig.add_annotation(
        x=76.2, y=60.1,
        text=f"库容   {float(storage):.2f}",
        showarrow=False,
        xanchor="left",
        font=dict(size=10.2, color=c_subtext)
    )
    fig.add_annotation(
        x=76.2, y=56.3,
        text=f"流量   {float(release):.2f}",
        showarrow=False,
        xanchor="left",
        font=dict(size=10.2, color=c_subtext)
    )
    fig.add_annotation(
        x=76.2, y=52.5,
        text=f"出力   {float(power):.2f} MW",
        showarrow=False,
        xanchor="left",
        font=dict(size=10.2, color=c_subtext)
    )

    # 底部状态栏
    bottom_text = (
        f"Storage={float(storage):.2f}  |  "
        f"Inflow={float(inflow):.2f} m³/s  |  "
        f"Release={float(release):.2f} m³/s  |  "
        f"Power={float(power):.2f} MW"
    )
    fig.add_annotation(
        x=50, y=4.0,
        text=bottom_text,
        showarrow=False,
        font=dict(size=10.5, color=c_subtext)
    )

    # =========================
    # 11) 布局（白底、无坐标轴、科研平台风）
    # =========================
    fig.update_layout(
        height=430,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        xaxis=dict(
            range=[0, 100],
            visible=False,
            fixedrange=True
        ),
        yaxis=dict(
            range=[0, 70],
            visible=False,
            fixedrange=True,
            scaleanchor="x",
            scaleratio=1
        ),
        showlegend=False,
        hovermode=False
    )

    return fig


def apply_clean_layout(fig, title, x_title, y_title, height=280):
    return apply_industrial_layout(fig, title, x_title, y_title, height=height)


def apply_industrial_layout(fig, title, x_title, y_title, height=300):
    fig.update_layout(
        title=dict(
            text=title,
            font=dict(size=17, color="#111827"),
            x=0.02
        ),
        height=height,
        margin=dict(l=20, r=20, t=48, b=24),

        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",

        font=dict(color="#1F2937"),

        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font=dict(color="#111827")
        ),

        xaxis=dict(
            title=x_title,
            gridcolor="rgba(0,0,0,0.08)",
            zerolinecolor="rgba(0,0,0,0.1)",
            tickfont=dict(color="#374151"),
            title_font=dict(color="#374151"),
        ),

        yaxis=dict(
            title=y_title,
            gridcolor="rgba(0,0,0,0.08)",
            zerolinecolor="rgba(0,0,0,0.1)",
            tickfont=dict(color="#374151"),
            title_font=dict(color="#374151"),
        ),

        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1F2937")
        )
    )

    return fig


def add_current_hour_marker(fig, hour):
    fig.add_vline(
        x=hour,
        line_width=1.6,
        line_dash="dash",
        line_color="#DC2626",
        annotation_text=f"{int(hour):02d}:00",
        annotation_position="top right",
        annotation_font=dict(color="#FFD166", size=10),
    )
    return fig


def line_chart(hours, y, title, yname, current_hour=None, color="#2563EB"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=y, mode="lines+markers",
        line=dict(width=3, color=color), marker=dict(size=6, color=color), name=yname
    ))
    if current_hour is not None:
        add_current_hour_marker(fig, current_hour)
    return apply_industrial_layout(fig, title, "小时", yname, height=280)


def multi_line_chart(hours, series_dict, title, yname, current_hour=None):
    fig = go.Figure()
    for name, y in series_dict.items():
        highlight = (name == "APSO-LS")
        fig.add_trace(go.Scatter(
            x=hours, y=y, mode="lines+markers", name=name,
            line=dict(width=4.2 if highlight else 2.1, color="#FFD166" if highlight else "#0A84FF"),
            opacity=1.0 if highlight else 0.38,
            marker=dict(size=6 if highlight else 4)
        ))
    if current_hour is not None:
        add_current_hour_marker(fig, current_hour)
    return apply_industrial_layout(fig, title, "小时", yname, height=310)


def build_revenue_smooth_dual_axis(results):
    names = list(results.keys())
    revenue = [results[k]["detail"]["revenue"] for k in names]
    smooth = [results[k]["detail"]["smooth_penalty"] for k in names]
    colors = ["#FFD166" if n == "APSO-LS" else "rgba(34,211,238,0.65)" for n in names]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=names, y=revenue, name="总收益", marker_color=colors))
    fig.add_trace(go.Scatter(
        x=names, y=smooth, name="波动惩罚", yaxis="y2",
        mode="lines+markers", line=dict(width=3, color="#2563EB"), marker=dict(size=7)
    ))

    fig.update_layout(
        yaxis2=dict(
            title="平滑惩罚",
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="#9fd8ff"),
            title_font=dict(color="#9fd8ff")
        )
    )
    return apply_industrial_layout(fig, "收益-波动双轴分析", "策略", "总收益(元)", height=320)


def build_strategy_contrast_chart(hours, results, current_hour=None):
    return multi_line_chart(
        hours,
        {k: results[k]["Q"] for k in results.keys()},
        "多策略对比强化图（APSO-LS高亮）",
        "出流(m³/s)",
        current_hour=current_hour
    )


def build_inflow_price_dual_axis(hours, inflow, price, current_hour=None):
    fig = go.Figure()
    fig.add_trace(go.Bar(x=hours, y=inflow, name="入流", marker_color="rgba(34,211,238,0.65)"))
    fig.add_trace(go.Scatter(
        x=hours, y=price, name="电价", yaxis="y2", mode="lines+markers",
        line=dict(width=3, color="#0A84FF")
    ))
    fig.update_layout(
        yaxis2=dict(
            title="电价",
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="#9fd8ff"),
            title_font=dict(color="#9fd8ff")
        )
    )
    if current_hour is not None:
        add_current_hour_marker(fig, current_hour)
    return apply_industrial_layout(fig, "入流 + 电价双轴图", "小时", "入流(m³/s)", height=300)


def build_storage_power_dual_axis(hours, storage_24, power, current_hour=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=storage_24, name="库容", mode="lines+markers",
        line=dict(width=3, color="#22D3EE")
    ))
    fig.add_trace(go.Bar(
        x=hours, y=power, name="出力", yaxis="y2",
        marker_color="rgba(10,132,255,0.55)"
    ))
    fig.update_layout(
        yaxis2=dict(
            title="出力(MW)",
            overlaying="y",
            side="right",
            showgrid=False,
            tickfont=dict(color="#9fd8ff"),
            title_font=dict(color="#9fd8ff")
        )
    )
    if current_hour is not None:
        add_current_hour_marker(fig, current_hour)
    return apply_industrial_layout(fig, "库容 + 出力双轴图", "小时", "库容", height=300)


def compare_bar(results):
    names = list(results.keys())
    revenues = [results[k]["detail"]["revenue"] for k in names]
    objectives = [results[k]["detail"]["objective"] for k in names]
    colors = ["#FFD166" if n == "APSO-LS" else "rgba(34,211,238,0.55)" for n in names]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=names, y=revenues, name="收益", marker_color=colors))
    fig.add_trace(go.Bar(x=names, y=objectives, name="综合目标", marker_color="rgba(10,132,255,0.55)"))
    fig.update_layout(barmode="group")
    return apply_industrial_layout(fig, "不同调度策略对比", "方法", "指标值", height=320)


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
            background: radial-gradient(circle at 18% 14%, #0f2f56 0%, #08182d 62%, #071220 100%);
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
            padding: 10px 12px;
            background: rgba(5,18,36,0.64);
            color: #dff6ff;
            font-size: 13px;
            line-height: 1.5;
            border-radius: 8px;
            border: 1px solid rgba(34, 211, 238, 0.35);
            z-index: 20;
            pointer-events: none;
            min-width: 130px;
            font-family: Arial, sans-serif;
        }
        #cameraPanel {
            position: absolute;
            right: 16px;
            top: 16px;
            display: flex;
            gap: 8px;
            z-index: 35;
            background: rgba(4, 14, 30, 0.56);
            border: 1px solid rgba(34,211,238,0.28);
            border-radius: 999px;
            padding: 6px;
            backdrop-filter: blur(6px);
        }
        .cam-btn {
            border: 1px solid rgba(34,211,238,0.35);
            background: rgba(10,132,255,0.16);
            color: #d6f5ff;
            border-radius: 999px;
            padding: 6px 10px;
            font-size: 12px;
            cursor: pointer;
        }
        .cam-btn.active {
            background: rgba(255, 209, 102, 0.18);
            border-color: rgba(255, 209, 102, 0.78);
            color: #ffe7ac;
            font-weight: 700;
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
    <div id="cameraPanel">
        <button class="cam-btn active" data-mode="dam">坝体</button>
        <button class="cam-btn" data-mode="reservoir">水库</button>
        <button class="cam-btn" data-mode="river">河道</button>
        <button class="cam-btn" data-mode="auto">自动巡航</button>
    </div>
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
        scene.background = new THREE.Color(0x071524);
        scene.fog = new THREE.Fog(0x0a1f35, 120, 360);

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

        const ambient = new THREE.AmbientLight(0xbadfff, 1.10);
        scene.add(ambient);

        const sun = new THREE.DirectionalLight(0xe8f5ff, 1.20);
        sun.position.set(120, 160, 80);
        scene.add(sun);

        const fill = new THREE.DirectionalLight(0x7dd8ff, 0.62);
        fill.position.set(-100, 90, -90);
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
        let visualWaterLevel = state.waterLevel;
        let visualQFactor = state.qFactor;
        let cameraMode = "dam";
        let autoCameraPhase = 0;

        let autoCamera = false;
        let autoAngle = 0;

        const cameraModes = {
            dam: {
                pos: new THREE.Vector3(150, 120, -20),
                target: new THREE.Vector3(0, 13, 0)
            },
            reservoir: {
                pos: new THREE.Vector3(-120, 85, 20),
                target: new THREE.Vector3(-55, 16, 0)
            },
            river: {
                pos: new THREE.Vector3(20, 200, 70),
                target: new THREE.Vector3(20, 15, 0)
            }
        };

  

        const cameraButtons = Array.from(document.querySelectorAll(".cam-btn"));
        
        function flyTo(preset){
            const startPos = camera.position.clone();
            const startTarget = controls.target.clone();
        
            let t = 0;
        
            function move(){
                t += 0.03;
                if (t >= 1) return;
        
                camera.position.lerpVectors(startPos, preset.pos, t);
                controls.target.lerpVectors(startTarget, preset.target, t);
        
                requestAnimationFrame(move);
            }
        
            move();
        }
        
        cameraButtons.forEach(function(btn){
            btn.addEventListener("click", function(){
                const mode = btn.dataset.mode || "dam";
        
                cameraButtons.forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
        
                if (mode === "auto"){
                    autoCamera = true;
                    return;
                } else {
                    autoCamera = false;
                }
        
                const preset = cameraModes[mode];
                if (preset){
                    flyTo(preset);
                }
            });
        });
       
        function updateInfoPanel() {
            infoPanel.innerHTML =
                "时刻: " + state.hour + "<br>" +
                "Q: " + state.Q.toFixed(1) + "<br>" +
                "S: " + state.S.toFixed(1) + "<br>" +
                "水位: " + visualWaterLevel.toFixed(2);
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

        let powerhouseGlow = null;
        const animatedWaterMats = [];

        function createWaterMaterial(opts) {
            const o = opts || {};
            const mat = new THREE.MeshStandardMaterial({
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
            animatedWaterMats.push(mat);
            return mat;
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
                color: 0x1a4f8f,
                opacity: 0.90,
                roughness: 0.2,
                metalness: 0.05,
                normalScale: new THREE.Vector2(1.2, 1.2),
                emissiveIntensity: 0.15
            });

            const mesh = new THREE.Mesh(geo, mat);
            mesh.renderOrder = 1;
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
            mesh.renderOrder = 1;
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
                emissiveIntensity: 0.09,
                roughness: 0.2,
                metalness: 0.05,
                normalScale: new THREE.Vector2(1.8, 1.8)
            });

            const mesh = new THREE.Mesh(geo, mat);
            mesh.renderOrder = 1;
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

        function addPowerhouseGlow() {
            powerhouseGlow = new THREE.Mesh(
                new THREE.SphereGeometry(3.2, 24, 24),
                new THREE.MeshStandardMaterial({
                    color: 0x88e8ff,
                    emissive: 0x1ac8ff,
                    emissiveIntensity: 0.25,
                    transparent: true,
                    opacity: 0.55,
                    roughness: 0.2,
                    metalness: 0.05
                })
            );
            powerhouseGlow.position.set(7.5, terrainHeight(7.5, 0) + 3.8, 0.5);
            staticGroup.add(powerhouseGlow);
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
        addPowerhouseGlow();
        addTreesNatural();
        loadDam();
        rebuildDynamicScene();
        updateInfoPanel();

        window.setDispatchHour = setDispatchHour;
        window.addEventListener("resize", onResize);

        const clock = new THREE.Clock();

        function animate() {
            requestAnimationFrame(animate);

            const dt = Math.min(clock.getDelta(), 0.05);
            visualWaterLevel += (state.waterLevel - visualWaterLevel) * 0.05;
            visualQFactor += (state.qFactor - visualQFactor) * 0.05;

            const flowOffsetX = (0.0018 + visualQFactor * 0.0075) * (dt * 60);
            const flowOffsetY = (0.0010 + visualQFactor * 0.0040) * (dt * 60);
            waterNormalTex.offset.x += flowOffsetX;
            waterNormalTex.offset.y += flowOffsetY;

            for (let i = 0; i < animatedWaterMats.length; i++) {
                animatedWaterMats[i].emissiveIntensity = 0.08 + visualQFactor * 0.20;
            }

            if (powerhouseGlow && powerhouseGlow.material) {
                powerhouseGlow.material.emissiveIntensity = 0.18 + visualQFactor * 1.15;
                powerhouseGlow.material.opacity = 0.38 + visualQFactor * 0.38;
            }

            updateInfoPanel();

        if (autoCamera){
            autoAngle += 0.003;
        
            const radius = 180;
        
            camera.position.x = Math.cos(autoAngle) * radius;
            camera.position.z = Math.sin(autoAngle) * radius;
            camera.position.y = 90 + Math.sin(autoAngle * 0.5) * 20;
        
            controls.target.set(0, 15, 0);
        }

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


def get_recommendation(results):
    best_name = max(results, key=lambda k: results[k]["detail"]["objective"])
    d = results[best_name]["detail"]
    reason = f"{best_name} 的综合目标函数最高（{d['objective']:.0f}），且兼顾收益与平稳性。"
    return best_name, reason

def generate_dispatch_advice(storage, inflow, release, power, params):
    advice = []

    level_ratio = (storage - params["S_min"]) / (params["S_max"] - params["S_min"] + 1e-9)

    if level_ratio > 0.85:
        advice.append({
            "type": "warning",
            "title": "高水位风险",
            "message": "建议增加下泄流量",
            "action": "increase_release"
        })

    elif level_ratio < 0.25:
        advice.append({
            "type": "warning",
            "title": "低水位运行",
            "message": "建议减少出库",
            "action": "reduce_release"
        })

    if inflow > release * 1.5:
        advice.append({
            "type": "alert",
            "title": "入流快速增加",
            "message": "建议提前预泄",
            "action": "pre_release"
        })

    if power < 50:
        advice.append({
            "type": "suggestion",
            "title": "发电偏低",
            "message": "可适当提高出流",
            "action": "increase_power"
        })

    return advice


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

    demo_speed = st.slider("演示速度（倍速）", min_value=0.5, max_value=3.0, value=float(st.session_state.demo_speed),
                           step=0.1)
    st.session_state.demo_speed = demo_speed

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
advice = generate_dispatch_advice(
    storage=detail["S"][hour],
    inflow=inflow[hour],
    release=Q[hour],
    power=detail["power_mw"][hour],
    params=params
)
if "action" in st.session_state and st.session_state["action"]:

    action = st.session_state["action"]

    if action == "increase_release":
        Q[hour] *= 1.1

    elif action == "reduce_release":
        Q[hour] *= 0.9

    elif action == "increase_power":
        Q[hour] *= 1.05

    elif action == "pre_release":
        Q[hour] *= 1.2

    st.session_state["action"] = None
hours = np.arange(24)
best_name, best_reason = get_recommendation(results)
table_data = build_result_table(results)

display_name = "APSO-LS" if best_name == "APSO-LS" else best_name

st.markdown("""
<div class="dashboard-title">
    <h1>🌊 智调水电：水电站智能优化调度与数字孪生仿真平台</h1>
    <p>面向新能源消纳的 24h 优化调度与三维联动仿真系统</p>
    <div class="status-chip-wrap">
        <div class="status-chip">🌊 三维水库-坝体联动</div>
        <div class="status-chip">⚡ 多目标优化调度</div>
        <div class="status-chip">📊 24小时动态演示</div>
        <div class="status-chip">🛰 数字孪生可视化</div>
    </div>
</div>
""", unsafe_allow_html=True)

top1, top2, top3, top4, top5 = st.columns(5)
best_rev = results[best_name]["detail"]["revenue"]
rev_delta = detail["revenue"] - best_rev
top1.metric("推荐策略", display_name)
top2.metric("当前策略", algo)
top3.metric("当前策略收益", f"{detail['revenue']:.0f} 元", delta=f"{rev_delta:.0f} vs 最优")
top4.metric("综合目标", f"{detail['objective']:.0f}",
            delta=f"{detail['objective'] - results[best_name]['detail']['objective']:.0f}")
top5.metric("当前时刻", f"{(hour if not auto_play else 0):02d}:00")

st.markdown(f'<div class="kpi-best">⭐ 最优策略高亮：<b>{best_name}</b> ｜ 收益 {best_rev:.0f} 元</div>',
            unsafe_allow_html=True)

if st.session_state.demo_mode:
    st.markdown('<div class="demo-running">🟢 DEMO RUNNING</div>', unsafe_allow_html=True)

st.success(f"系统推荐：{best_name}。{best_reason}")

st.markdown("### 🧠 调度决策建议")

if not advice:
    st.success("✔ 当前状态良好，无需调整")
else:
    cols = st.columns(len(advice))

    for i, a in enumerate(advice):
        with cols[i]:
            if a["type"] == "alert":
                st.error(f"🚨 {a['title']}")
            elif a["type"] == "warning":
                st.warning(f"⚠ {a['title']}")
            else:
                st.info(f"💡 {a['title']}")

            st.caption(a["message"])

            if st.button("执行", key=f"act_{i}"):
                st.session_state["action"] = a["action"]

with st.expander("系统说明", expanded=False):
    st.write(
        "本系统集成入流与电价数据输入、多目标优化求解、调度策略对比、运行状态展示与三维可视化仿真功能。"
        "当前版本在现有稳定系统基础上进行工程级升级，本步骤仅优化整体页面结构与大屏视觉布局，不改变算法与数据驱动主链路。"
    )

alerts = build_alerts(detail, params, hour if not auto_play else 0)
for msg in alerts:
    st.info(msg)

st.markdown("""
<style>

/* ===== 全局文字强化 ===== */

h1, h2, h3, h4 {
    color: #111827 !important;
}

.panel-title {
    color: #111827 !important;
}

.main-3d-title-left {
    color: #111827 !important;
}

.status-chip {
    color: #111827 !important;
    background: #E6F4FF !important;
    border: 1px solid #93C5FD !important;
}

.analysis-title {
    color: #111827 !important;
}

.panel-card b,
.panel-card strong {
    color: #111827 !important;
}

.kpi-best {
    color: #92400E !important;
}

.stAlert {
    color: #111827 !important;
}

</style>
""", unsafe_allow_html=True)

def render_dashboard_main(hour, strategy_override=None):
    current_algo = strategy_override if strategy_override is not None else algo
    current_result = results[current_algo]
    current_Q = current_result["Q"]
    current_detail = current_result["detail"]

    left_col, center_col, right_col = st.columns([1.05, 3.2, 1.15], gap="medium")

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
                line_chart(hours, current_Q, f"{current_algo} 调度出流曲线", "出流(m³/s)", current_hour=hour,
                           color="#22D3EE"),
                width="stretch"
            )

        with trend2:
            st.plotly_chart(
                line_chart(np.arange(25), current_detail["S"], f"{current_algo} 库容变化曲线", "库容",
                           current_hour=hour, color="#0A84FF"),
                width="stretch"
            )

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="analysis-title">📈 深度分析区</div>', unsafe_allow_html=True)
        a1, a2 = st.columns(2)
        with a1:
            st.plotly_chart(build_inflow_price_dual_axis(hours, inflow, price, current_hour=hour), width="stretch")
        with a2:
            st.plotly_chart(build_strategy_contrast_chart(hours, results, current_hour=hour), width="stretch")

        b1, b2 = st.columns(2)
        with b1:
            st.plotly_chart(
                build_storage_power_dual_axis(hours, current_detail["S"][:-1], current_detail["power_mw"],
                                              current_hour=hour),
                width="stretch"
            )
        with b2:
            st.plotly_chart(build_revenue_smooth_dual_axis(results), width="stretch")

    with right_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">KPI 指标看板</div>', unsafe_allow_html=True)
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


strategies = ["Rule", "PSO", "APSO-LS", "GA"]

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

    time.sleep(max(0.12, 0.6 / max(0.1, st.session_state.demo_speed)))
    st.rerun()

if page_mode == "单策略分析":
    if auto_play and scene_mode == "2D场景":
        t = st.session_state.play_hour
        render_dashboard_main(t)
        st.session_state.play_hour = (t + 1) % 24
        time.sleep(max(0.12, 0.5 / max(0.1, st.session_state.demo_speed)))
        st.rerun()
    else:
        st.session_state.play_hour = hour
        render_dashboard_main(hour)

    st.markdown("---")

    row_a1, row_a2 = st.columns(2)
    with row_a1:
        st.plotly_chart(
            line_chart(hours, inflow, "24小时入流曲线", "入流(m³/s)", current_hour=hour, color="#22D3EE"),
            width="stretch"
        )
    with row_a2:
        st.plotly_chart(
            line_chart(hours, price, "24小时电价曲线", "电价", current_hour=hour, color="#0A84FF"),
            width="stretch"
        )

    row_b1, row_b2 = st.columns(2)
    with row_b1:
        st.plotly_chart(
            line_chart(hours, detail["power_mw"], f"{algo} 出力曲线", "功率(MW)", current_hour=hour, color="#22D3EE"),
            width="stretch"
        )
    with row_b2:
        st.plotly_chart(
            line_chart(hours, detail["cum_revenue"], f"{algo} 累计收益曲线", "累计收益(元)", current_hour=hour,
                       color="#F59E0B"),
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
            "出流(m³/s)",
            current_hour=hour
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
                "库容",
                current_hour=hour
            ),
            width="stretch"
        )
    with compare_c2:
        st.plotly_chart(
            multi_line_chart(
                hours,
                {k: results[k]["detail"]["power_mw"] for k in results.keys()},
                "不同策略出力曲线对比",
                "功率(MW)",
                current_hour=hour
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