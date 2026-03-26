import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="智调水电Demo", layout="wide")


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
        # 1) 基础出流
        q_base = 0.98 * inflow[t]

        # 2) 电价修正
        price_z = (price[t] - price_mean) / price_std
        q_price = 40.0 * price_z

        # 3) 库容修正
        storage_ratio = (S[t] - S_min) / (S_max - S_min + 1e-6)
        q_storage = 55.0 * (storage_ratio - 0.5)

        q = q_base + q_price + q_storage
        q = np.clip(q, Q_min, Q_max)

        # 4) 平滑
        if t > 0:
            q = 0.7 * Q[t - 1] + 0.3 * q

        Q[t] = q

        # 更新库容
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

    fig.add_annotation(x=50, y=28, text="某某河水库", showarrow=False, font=dict(size=22, color="#ffffff"))
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
    """
    Plotly 3D 场景版：
    - Surface: 山谷地形 + 水面
    - Mesh3d: 坝体 + 厂房
    """
    s_min = params["S_min"]
    s_max = params["S_max"]

    level_ratio = (storage - s_min) / (s_max - s_min)
    level_ratio = float(np.clip(level_ratio, 0.08, 0.98))

    # ----------------------------
    # 1) 构造山谷地形
    # ----------------------------
    x = np.linspace(-10, 10, 70)
    y = np.linspace(-6, 16, 90)
    X, Y = np.meshgrid(x, y)

    # 做一个“河谷 + 两侧山体”
    valley = 0.18 * (X ** 2) + 0.015 * (Y - 4) ** 2
    slope = 0.18 * (16 - Y)  # 上游更高、下游更低
    Z_terrain = 26 + valley + slope

    # 河道再压低一点
    channel = np.exp(-(X / 2.4) ** 2) * (5.5 + 0.12 * (16 - Y))
    Z_terrain = Z_terrain - channel

    # ----------------------------
    # 2) 水面高度（跟库容联动）
    # ----------------------------
    water_level = 29 + 7.5 * level_ratio

    # 水面覆盖区域：坝前上游区域
    water_mask = (np.abs(X) < 3.2 + 0.05 * (16 - Y)) & (Y <= 12.2)
    Z_water = np.where(water_mask, water_level, np.nan)

    # ----------------------------
    # 3) 创建图
    # ----------------------------
    fig = go.Figure()

    # 地形 surface
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

    # 水面 surface
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

    # ----------------------------
    # 4) 坝体 Mesh3d
    # ----------------------------
    # 一个简化的梯形坝体
    dam_vertices = np.array([
        [-2.2, 12.2, 24.5],   # 0 前左下
        [ 2.2, 12.2, 24.5],   # 1 前右下
        [-1.6, 12.2, 36.5],   # 2 前左上
        [ 1.6, 12.2, 36.5],   # 3 前右上

        [-2.8, 13.4, 23.8],   # 4 后左下
        [ 2.8, 13.4, 23.8],   # 5 后右下
        [-2.0, 13.4, 37.2],   # 6 后左上
        [ 2.0, 13.4, 37.2],   # 7 后右上
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

    # ----------------------------
    # 5) 厂房 Mesh3d
    # ----------------------------
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

    # ----------------------------
    # 6) 坝前水位线（3D line）
    # ----------------------------
    fig.add_trace(go.Scatter3d(
        x=np.linspace(-2.6, 2.6, 40),
        y=np.full(40, 11.6),
        z=np.full(40, water_level),
        mode="lines",
        line=dict(color="#1f77b4", width=6, dash="dash"),
        hoverinfo="skip",
        showlegend=False
    ))

    # ----------------------------
    # 7) 入流 / 泄流箭头（用 3D 线近似）
    # ----------------------------
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

    # ----------------------------
    # 8) 关键标注
    # ----------------------------
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

    # ----------------------------
    # 9) 布局与视角
    # ----------------------------
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


def line_chart(hours, y, title, yname):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hours, y=y, mode="lines+markers",
        line=dict(width=3), marker=dict(size=6)
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

    auto_play = st.checkbox("自动播放 24h", value=False)

    # 放在 auto_play 定义之后
    if scene_mode != "2D场景" and auto_play:
        st.warning("3D场景不建议自动播放，建议使用 2D 场景或关闭自动播放。")

    if not auto_play:
        hour = st.slider("当前时刻", 0, 23, 16, 1)
    else:
        hour = 0


# =========================================================
# 6. 主界面
# =========================================================
inflow, price, params, results = run_all_methods(
    seed, beta_smooth, s0, smin, smax, qmin, qmax, head, eta
)
selected = results[algo]
Q = selected["Q"]
detail = selected["detail"]
hours = np.arange(24)
best_name, best_reason = get_recommendation(results)

st.title("“智调水电”——水电站智能优化调度可视化仿真平台")
st.caption("面向新能源消纳的演示系统")

c_top1, c_top2, c_top3, c_top4 = st.columns(4)
display_name = "APSO-LS" if best_name == "APSO-LS" else best_name
c_top1.metric("推荐策略", display_name)
c_top2.metric("当前策略收益", f"{detail['revenue']:.0f} 元")
c_top3.metric("当前策略综合目标", f"{detail['objective']:.0f}")
c_top4.metric("平滑权重 β", f"{beta_smooth:.1f}")

st.success(f"系统推荐：{best_name}。{best_reason}")

with st.expander("系统说明", expanded=False):
    st.write(
        "本系统集成入流与电价数据输入、多目标优化求解、调度策略对比、运行状态展示与可视化仿真功能，"
        "可用于水电站日内调度方案分析与决策辅助。"
    )

alerts = build_alerts(detail, params, hour if not auto_play else 0)
for msg in alerts:
    st.info(msg)


def render_main(t):
    c1, c2, c3 = st.columns([1.0, 2.5, 1.0])

    with c1:
        st.subheader("实时运行指标")
        st.metric("当前时刻", f"{t:02d}:00")
        st.metric("入流量", f"{inflow[t]:.2f} m³/s")
        st.metric("下泄流量", f"{Q[t]:.2f} m³/s")
        st.metric("机组出力", f"{detail['power_mw'][t]:.2f} MW")
        st.metric("当前库容", f"{detail['S'][t]:.2f}")
        st.metric("累计收益", f"{detail['cum_revenue'][t]:.0f} 元")

    with c2:
        if scene_mode == "2D场景":
            st.subheader("二维水库仿真场景")
            fig_2d = build_reservoir_scene_2d(
                storage=detail["S"][t],
                params=params,
                release=Q[t],
                inflow=inflow[t],
                power=detail["power_mw"][t],
                hour=t
            )
            st.plotly_chart(
                fig_2d,
                width="stretch",
                config={"displayModeBar": False}
            )

        elif scene_mode == "3D场景":
            st.subheader("三维水库仿真场景")
            fig_3d = build_reservoir_scene(
                storage=detail["S"][t],
                params=params,
                release=Q[t],
                inflow=inflow[t],
                power=detail["power_mw"][t],
                hour=t
            )
            st.plotly_chart(
                fig_3d,
                width="stretch",
                config={"displayModeBar": True}
            )

        else:
            st.subheader("二维/三维对照场景")
            sub1, sub2 = st.columns(2)

            with sub1:
                fig_2d = build_reservoir_scene_2d(
                    storage=detail["S"][t],
                    params=params,
                    release=Q[t],
                    inflow=inflow[t],
                    power=detail["power_mw"][t],
                    hour=t
                )
                st.plotly_chart(
                    fig_2d,
                    width="stretch",
                    config={"displayModeBar": False}
                )

            with sub2:
                fig_3d = build_reservoir_scene(
                    storage=detail["S"][t],
                    params=params,
                    release=Q[t],
                    inflow=inflow[t],
                    power=detail["power_mw"][t],
                    hour=t
                )
                st.plotly_chart(
                    fig_3d,
                    width="stretch",
                    config={"displayModeBar": True}
                )

    with c3:
        st.subheader("方案总体指标")
        st.metric("总收益", f"{detail['revenue']:.0f} 元")
        st.metric("平滑指标", f"{detail['smooth_penalty']:.2f}")
        st.metric("弃水量", f"{detail['spill']:.4f}")
        st.metric("综合目标", f"{detail['objective']:.0f}")


if page_mode == "单策略分析":
    if auto_play and scene_mode == "2D场景":
        placeholder = st.empty()
        for t in range(24):
            with placeholder.container():
                render_main(t)
            time.sleep(0.35)
    else:
        render_main(hour)

    st.markdown("---")

    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.plotly_chart(line_chart(hours, inflow, "24小时入流曲线", "入流(m³/s)"), width="stretch")
    with r1c2:
        st.plotly_chart(line_chart(hours, price, "24小时电价曲线", "电价"), width="stretch")

    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.plotly_chart(line_chart(hours, Q, f"{algo} 调度出流曲线", "出流(m³/s)"), width="stretch")
    with r2c2:
        st.plotly_chart(line_chart(np.arange(25), detail["S"], f"{algo} 库容变化曲线", "库容"), width="stretch")

    r3c1, r3c2 = st.columns(2)
    with r3c1:
        st.plotly_chart(line_chart(hours, detail["power_mw"], f"{algo} 出力曲线", "功率(MW)"), width="stretch")
    with r3c2:
        st.plotly_chart(line_chart(hours, detail["cum_revenue"], f"{algo} 累计收益曲线", "累计收益(元)"), width="stretch")

    hist = results[algo]["history"]
    if hist is not None:
        st.plotly_chart(
            line_chart(np.arange(len(hist)), hist, f"{algo} 收敛过程", "目标函数"),
            width="stretch"
        )

else:
    st.subheader("多策略运行对比")

    compare_hour = hour if not auto_play else 12
    cc1, cc2, cc3, cc4 = st.columns(4)
    for col, name in zip([cc1, cc2, cc3, cc4], results.keys()):
        d = results[name]["detail"]
        col.metric(
            name,
            f"{d['revenue']:.0f} 元",
            delta=f"Obj={d['objective']:.0f}"
        )

    st.plotly_chart(
        multi_line_chart(
            hours,
            {k: results[k]["Q"] for k in results.keys()},
            "不同策略出流曲线对比",
            "出流(m³/s)"
        ),
        width="stretch"
    )

    c_compare1, c_compare2 = st.columns(2)
    with c_compare1:
        st.plotly_chart(
            multi_line_chart(
                np.arange(25),
                {k: results[k]["detail"]["S"] for k in results.keys()},
                "不同策略库容变化对比",
                "库容"
            ),
            width="stretch"
        )
    with c_compare2:
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

st.markdown("---")

table_data = pd.DataFrame({
    "方法": list(results.keys()),
    "收益 Revenue": [results[k]["detail"]["revenue"] for k in results.keys()],
    "平滑指标 Smooth": [results[k]["detail"]["smooth_penalty"] for k in results.keys()],
    "弃水量 Spill": [results[k]["detail"]["spill"] for k in results.keys()],
    "综合目标 Objective": [results[k]["detail"]["objective"] for k in results.keys()],
})
table_data["推荐"] = table_data["方法"].apply(lambda x: "是" if x == best_name else "")
st.subheader("调度方案评价表")
st.dataframe(table_data, width="stretch")

csv_bytes = table_data.to_csv(index=False).encode("utf-8-sig")
st.download_button(
    "下载评价表 CSV",
    data=csv_bytes,
    file_name="hydro_dispatch_results.csv",
    mime="text/csv"
)