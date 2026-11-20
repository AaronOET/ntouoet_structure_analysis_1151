"""梁的斜率與撓度 — 集中載重位置可調的互動示範。

支援三種靜定梁（EI 為常數）：
    'simple'      簡支梁：A 鉸支承、B 滾支承
    'cantilever'  懸臂梁：A 固定端，右端自由
    'overhang'    外伸梁：A 鉸支承、B 滾支承，B 右側外伸

在 notebook 中使用：
    from beam_deflection import demo
    demo('simple')

符號規定（與課本相同）：
    v 向上為正（向下的撓度為負值），θ = dv/dx 逆時針為正，
    彎矩 M 使梁下緣受拉（正彎矩）為正，EI d²v/dx² = M(x)。
單位：P (kN)、長度 (m)、EI (kN·m²)；θ 以 rad、v 以 mm 顯示。
"""
from functools import lru_cache

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import ipywidgets as widgets
from IPython.display import display, Math

from cjk_font import setup_cjk_font

# 中文字型（本機用已安裝字型；Colab / Binder 會自動下載 Noto Sans TC）
setup_cjk_font()

# 各種梁的幾何：L 為全長，LB 為 A 到 B 支承的距離（懸臂梁沒有 B）
BEAMS = {
    'simple':     dict(L=10.0, LB=10.0, name='簡支梁', a0=3.0, probe0=5.0),
    'cantilever': dict(L=6.0,  LB=None, name='懸臂梁', a0=6.0, probe0=6.0),
    'overhang':   dict(L=12.0, LB=8.0,  name='外伸梁', a0=12.0, probe0=12.0),
}
P0 = 10.0        # 預設載重 (kN，向下)
EI0 = 20000.0    # 預設 EI (kN·m²)
N_PTS = 1201     # 繪圖取樣點數


# ---------------------------------------------------------------- 力學計算

def reactions(kind, a, P):
    """支承反力（向上為正、M_A 逆時針為正）。"""
    b = BEAMS[kind]
    if kind == 'cantilever':
        return {'Ay': P, 'MA': P * a}
    LB = b['LB']
    return {'Ay': P * (LB - a) / LB, 'By': P * a / LB}


def _loads(kind, a, P):
    """梁上所有外力：forces = [(F 向上為正, x0)]，couples = [(C 逆時針為正, x0)]。"""
    R = reactions(kind, a, P)
    forces = [(R['Ay'], 0.0), (-P, a)]
    couples = []
    if kind == 'cantilever':
        couples.append((R['MA'], 0.0))
    else:
        forces.append((R['By'], BEAMS[kind]['LB']))
    return forces, couples


def _mac(x, x0, n):
    """Macaulay 函數 ⟨x - x0⟩^n。"""
    d = np.asarray(x, dtype=float) - x0
    return np.where(d >= 0, np.maximum(d, 0) ** n, 0.0)


def _particular(kind, a, P, x):
    """不含積分常數的 EI·M、EI·θ、EI·v（由 Macaulay 函數逐項積分）。"""
    forces, couples = _loads(kind, a, P)
    M = sum(F * _mac(x, x0, 1) for F, x0 in forces) - sum(C * _mac(x, x0, 0) for C, x0 in couples)
    th = sum(F * _mac(x, x0, 2) / 2 for F, x0 in forces) - sum(C * _mac(x, x0, 1) for C, x0 in couples)
    v = sum(F * _mac(x, x0, 3) / 6 for F, x0 in forces) - sum(C * _mac(x, x0, 2) / 2 for C, x0 in couples)
    return M, th, v


def constants(kind, a, P):
    """由邊界條件求積分常數 C1、C2（EI θ = … + C1，EI v = … + C1 x + C2）。"""
    if kind == 'cantilever':
        bcs = [('theta', 0.0), ('v', 0.0)]          # 固定端：θ(0) = 0、v(0) = 0
    else:
        bcs = [('v', 0.0), ('v', BEAMS[kind]['LB'])]  # 兩支承：v(0) = 0、v(L_AB) = 0
    A, rhs = [], []
    for typ, xb in bcs:
        _, th, v = _particular(kind, a, P, xb)
        if typ == 'theta':
            A.append([1.0, 0.0]); rhs.append(-float(th))
        else:
            A.append([xb, 1.0]); rhs.append(-float(v))
    C1, C2 = np.linalg.solve(np.array(A), np.array(rhs))
    return C1, C2


def solve(kind, a, P, EI, x):
    """回傳 x 處的 M (kN·m)、θ (rad)、v (m)。"""
    C1, C2 = constants(kind, a, P)
    M, th, v = _particular(kind, a, P, x)
    x = np.asarray(x, dtype=float)
    return M, (th + C1) / EI, (v + C1 * x + C2) / EI


@lru_cache(maxsize=32)
def _envelope(kind, P, EI):
    """載重走遍全梁時 |M|、|θ|、|v| 的最大值，用來固定座標軸，方便比較不同載重位置。"""
    L = BEAMS[kind]['L']
    xs = np.linspace(0, L, 241)
    mm = tm = vm = 0.0
    for a in np.linspace(0, L, 61):
        M, th, v = solve(kind, a, P, EI, xs)
        mm, tm, vm = max(mm, np.abs(M).max()), max(tm, np.abs(th).max()), max(vm, np.abs(v).max())
    return mm or 1.0, tm or 1.0, vm or 1.0


def textbook_check(kind, a, P, EI):
    """課本公式（載重點下方的撓度等），回傳 (說明 LaTeX, 數值 v (m)) 或 None。"""
    b = BEAMS[kind]
    L, LB = b['L'], b['LB']
    if kind == 'cantilever':
        v = -P * a ** 2 * (3 * L - a) / (6 * EI)
        return (rf'v_{{\text{{自由端}}}} = -\dfrac{{P a^2 (3L - a)}}{{6EI}}'
                rf' = -\dfrac{{{P:g}({a:.2f})^2(3\cdot{L:g} - {a:.2f})}}{{6({EI:g})}}', v, L)
    if a <= LB:   # 載重在 AB 跨內：與簡支梁相同
        bb = LB - a
        v = -P * a ** 2 * bb ** 2 / (3 * EI * LB)
        return (rf'v_{{\text{{載重點}}}} = -\dfrac{{P a^2 b^2}}{{3EIL}}'
                rf' = -\dfrac{{{P:g}({a:.2f})^2({bb:.2f})^2}}{{3({EI:g})({LB:g})}}', v, a)
    c = a - LB    # 載重在外伸段
    v = -P * c ** 2 * (LB + c) / (3 * EI)
    return (rf'v_{{\text{{載重點}}}} = -\dfrac{{P c^2 (L_{{AB}} + c)}}{{3EI}}'
            rf' = -\dfrac{{{P:g}({c:.2f})^2({LB:g} + {c:.2f})}}{{3({EI:g})}}', v, a)


# ---------------------------------------------------------------- LaTeX

def _signed(coef, div, body, first=False):
    r"""把 (coef/div)·body 寫成「 + \frac{7}{6} body」或「 - 5 body」。"""
    if abs(coef) < 1e-12:
        return ''
    sign = '-' if coef < 0 else ('' if first else '+')
    q = abs(coef) / div
    if abs(q - round(q)) < 1e-9:
        c = f'{round(q):d}'
    elif div == 1:
        c = f'{q:.4g}'
    else:
        c = rf'\frac{{{abs(coef):.4g}}}{{{div}}}'
    return rf' {sign} {c}{body}'


def _bracket_tex(x0, n):
    if x0 == 0:
        return 'x' if n == 1 else f'x^{n}' if n > 1 else ''
    s = rf'\langle x - {x0:g}\rangle'
    return s if n == 1 else s + f'^{n}' if n > 1 else s + '^0'


def _equation_tex(kind, a, P, order):
    """order = 0: M(x)，1: EIθ，2: EIv（不含積分常數）。"""
    L = BEAMS[kind]['L']
    forces, couples = _loads(kind, a, P)
    div = {0: 1, 1: 2, 2: 6}[order]
    terms = []
    for F, x0 in forces:
        if x0 >= L:    # 位於梁右端的力在 0 ≤ x ≤ L 內不起作用
            continue
        terms.append((F, div, _bracket_tex(x0, order + 1)))
    for C, x0 in couples:
        cdiv = {0: 1, 1: 1, 2: 2}[order]
        terms.append((-C, cdiv, _bracket_tex(x0, order)))
    out = ''
    for c, d, body in terms:
        body = rf'\,{body}' if body else ''
        out += _signed(c, d, body, first=(out == ''))
    return out or '0'


# ---------------------------------------------------------------- 繪圖

def _draw_support(ax, x0, kind):
    ax.add_patch(plt.Polygon([[x0, 0], [x0 - 0.25, -0.45], [x0 + 0.25, -0.45]],
                             closed=True, fc='white', ec='k', lw=1.2, zorder=3))
    if kind == 'roller':
        for dx in (-0.15, 0.15):
            ax.add_patch(plt.Circle((x0 + dx, -0.55), 0.09, fc='white', ec='k', lw=1, zorder=3))
        ax.plot([x0 - 0.4, x0 + 0.4], [-0.66, -0.66], 'k', lw=1)
    else:
        ax.plot([x0 - 0.4, x0 + 0.4], [-0.46, -0.46], 'k', lw=1)


def _draw_wall(ax):
    ax.add_patch(plt.Rectangle((-0.35, -1.0), 0.35, 2.0, fc='#dddddd', ec='none', hatch='///', zorder=1))
    ax.plot([0, 0], [-1.0, 1.0], 'k', lw=1.5)


def _vertical_force(ax, x0, F, base, scale, color, label, ha):
    """在 x0 畫垂直力：F > 0 向上（由下往上指向 base），F < 0 向下。"""
    if abs(F) > 1e-9:
        tip, tail = base, base - 0.4 - scale * abs(F)
        if F < 0:
            tip, tail = tail, tip
        ax.annotate('', xy=(x0, tip), xytext=(x0, tail),
                    arrowprops=dict(arrowstyle='-|>', lw=2.5, color=color, mutation_scale=18))
    dx = -0.3 if ha == 'right' else 0.3
    ax.text(x0 + dx, base - 0.6, f'{label} = {F:.2f} kN', ha=ha, fontsize=10, color=color)


def _draw_beam(ax, kind, a, P, EI, probe, show_curve):
    """上圖：梁、載重、反力與（放大的）彈性曲線。"""
    b = BEAMS[kind]
    L, LB = b['L'], b['LB']
    R = reactions(kind, a, P)
    _, _, vmax = _envelope(kind, P, EI)
    scale = 1.0 / vmax            # 全域最大撓度畫成 1 個單位高

    ax.add_patch(plt.Rectangle((0, -0.08), L, 0.16, fc='#e6e6e6', ec='#999999', zorder=2))
    if kind == 'cantilever':
        _draw_wall(ax)
        _vertical_force(ax, 0.0, R['Ay'], -1.1, 1.0 / P, 'navy', r'$A_y$', 'left')
        ax.add_patch(FancyArrowPatch((-0.7, -0.6), (-0.7, 0.7), connectionstyle='arc3,rad=-0.5',
                                     arrowstyle='-|>', mutation_scale=15, lw=2.2, color='navy'))
        ax.text(-1.0, 0.75, rf'$M_A$ = {R["MA"]:.2f} kN·m', ha='right', fontsize=10, color='navy')
    else:
        _draw_support(ax, 0, 'pin')
        _draw_support(ax, LB, 'roller')
        _vertical_force(ax, 0, R['Ay'], -0.75, 1.2 / P, 'navy', r'$A_y$', 'right')
        _vertical_force(ax, LB, R['By'], -0.75, 1.2 / P, 'navy', r'$B_y$', 'left')
        ax.text(LB + 0.1, 0.3, 'B', fontsize=13)
    ax.text(-0.1 if kind != 'cantilever' else 0.1, 0.3, 'A', fontsize=13,
            ha='right' if kind != 'cantilever' else 'left')

    xs = np.linspace(0, L, N_PTS)
    _, _, v = solve(kind, a, P, EI, xs)
    va = float(solve(kind, a, P, EI, a)[2])
    y_load = va * scale if show_curve else 0.0
    if show_curve:
        ax.plot(xs, v * scale, color='#1f77b4', lw=3, zorder=4, label='彈性曲線（放大顯示）')
        vp = float(solve(kind, a, P, EI, probe)[2])
        ax.plot([probe], [vp * scale], 's', color='darkorange', ms=8, zorder=6)
        ax.text(L + 2.3, -3.0, f'撓度放大約 {scale:.0f} 倍', ha='right', fontsize=9, color='#1f77b4')

    # 集中載重 P（箭頭指到變形後的位置）
    ax.annotate('', xy=(a, y_load + 0.1), xytext=(a, y_load + 1.5),
                arrowprops=dict(arrowstyle='-|>', lw=2.5, color='crimson', mutation_scale=20))
    ax.text(a + 0.15, y_load + 1.3, f'P = {P:g} kN', color='crimson', fontsize=11, fontweight='bold')
    if a > 0.05:
        ax.annotate('', xy=(a, 2.25), xytext=(0, 2.25), arrowprops=dict(arrowstyle='<->', lw=1))
    ax.text(a / 2, 2.35, f'a = {a:g} m', ha='center', fontsize=10)

    ax.set_xlim(-2.4, L + 2.4)
    ax.set_ylim(-3.3, 2.7)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'{b["name"]}：載重、反力與彈性曲線', fontsize=11)


def _decorate(ax, kind, a, probe, ylabel, title, lim):
    b = BEAMS[kind]
    ax.axhline(0, color='k', lw=1)
    ax.axvline(a, color='crimson', lw=0.8, ls=':')
    ax.axvline(probe, color='darkorange', lw=0.8, ls='--')
    if b['LB'] is not None and b['LB'] < b['L']:
        ax.axvline(b['LB'], color='gray', lw=0.8, ls=':')
    ax.set_xlim(-0.3, b['L'] + 0.3)
    ax.set_ylim(-1.2 * lim, 1.2 * lim)
    ax.set_xticks(np.arange(0, b['L'] + 0.1, 1 if b['L'] <= 6 else 2))
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11)
    ax.grid(alpha=0.3)


def _label_point(ax, x, y, text, L, color):
    """在點旁標註文字；靠近右端時改放左側，避免超出圖框。"""
    right = x > 0.75 * L
    ax.annotate(text, (x, y), xytext=(-8 if right else 8, 6), textcoords='offset points',
                ha='right' if right else 'left', fontsize=9, color=color,
                bbox=dict(fc='white', ec='none', alpha=0.8, pad=1))


def plot_state(kind, a, P, EI, probe, show_curve=True):
    """畫出某一載重位置的梁、M、θ、v 圖。"""
    L = BEAMS[kind]['L']
    xs = np.unique(np.r_[np.linspace(0, L, N_PTS), a, probe])
    M, th, v = solve(kind, a, P, EI, xs)
    th_mr, v_mm = th * 1e3, v * 1e3
    Mlim, tlim, vlim = _envelope(kind, P, EI)
    i_max = int(np.argmax(np.abs(v)))
    _, th_p, v_p = solve(kind, a, P, EI, probe)
    th_p, v_p = float(th_p) * 1e3, float(v_p) * 1e3
    # θ 變號處（梁內部）= 撓度的極值點
    tol = 1e-9 * max(np.abs(th).max(), 1e-30)
    sgn = np.sign(np.where(np.abs(th) < tol, 0, th))
    idx = [k for k in range(1, len(xs) - 1) if sgn[k - 1] * sgn[k + 1] < 0 and sgn[k - 1] != sgn[k]]
    x_ext = xs[idx]
    v_ext = v_mm[idx]

    fig, axes = plt.subplots(4, 1, figsize=(7.5, 10.5),
                             gridspec_kw={'height_ratios': [1.0, 0.8, 0.8, 0.9]})
    _draw_beam(axes[0], kind, a, P, EI, probe, show_curve)

    ax = axes[1]
    ax.fill_between(xs, M, color='#d9d2f2')
    ax.plot(xs, M, color='#6a51a3', lw=2)
    _decorate(ax, kind, a, probe, 'M (kN·m)', '彎矩圖 M(x)（M/EI 即曲率）', Mlim)

    ax = axes[2]
    ax.fill_between(xs, th_mr, color='#d4ecd4')
    ax.plot(xs, th_mr, color='#2ca02c', lw=2)
    ax.plot(x_ext, np.zeros_like(x_ext), 'o', mfc='white', mec='#1f77b4', ms=8, zorder=5)
    ax.plot([probe], [th_p], 's', color='darkorange', ms=8, zorder=6)
    _label_point(ax, probe, th_p, rf'$\theta$ = {th_p:.3f}', L, 'darkorange')
    _decorate(ax, kind, a, probe, r'$\theta$ ($10^{-3}$ rad)',
              r'斜率 $\theta(x) = dv/dx$（逆時針為正；空心圓：$\theta = 0$）', tlim * 1e3)

    ax = axes[3]
    ax.fill_between(xs, v_mm, color='#cfe3f3')
    ax.plot(xs, v_mm, color='#1f77b4', lw=2.5)
    ax.plot(x_ext, v_ext, 'o', mfc='white', mec='#1f77b4', ms=8, zorder=5)
    ax.plot([xs[i_max]], [v_mm[i_max]], 'o', color='#1f77b4', ms=8, zorder=5)
    ax.text(0.01, 0.04, f'最大 |v| = {abs(v_mm[i_max]):.2f} mm，位於 x = {xs[i_max]:.2f} m',
            transform=ax.transAxes, fontsize=9, color='#1f77b4',
            bbox=dict(fc='white', ec='#1f77b4', alpha=0.9, boxstyle='round,pad=0.3'))
    ax.plot([probe], [v_p], 's', color='darkorange', ms=8, zorder=6)
    _label_point(ax, probe, v_p, f'v = {v_p:.2f}', L, 'darkorange')
    _decorate(ax, kind, a, probe, 'v (mm)', '撓度 v(x)（向上為正）', vlim * 1e3)
    ax.set_xlabel('x (m)')

    plt.tight_layout()
    plt.show()


def show_working(kind, a, P, EI, probe):
    """以 Macaulay 函數列出積分法的計算過程與課本公式的檢核。"""
    b = BEAMS[kind]
    R = reactions(kind, a, P)
    C1, C2 = constants(kind, a, P)
    _, th_p, v_p = solve(kind, a, P, EI, probe)

    if kind == 'cantilever':
        display(Math(rf'+\uparrow\Sigma F_y = 0:\ A_y = P = {R["Ay"]:g}\ \text{{kN}},\qquad'
                     rf'\circlearrowleft +\Sigma M_A = 0:\ M_A - {P:g}({a:.2f}) = 0'
                     rf'\ \Rightarrow\ M_A = {R["MA"]:.3f}\ \text{{kN·m}}'))
    else:
        LB = b['LB']
        display(Math(rf'\circlearrowleft +\Sigma M_A = 0:\ B_y({LB:g}) - {P:g}({a:.2f}) = 0'
                     rf'\ \Rightarrow\ B_y = {R["By"]:.3f},\qquad A_y = {P:g} - B_y = {R["Ay"]:.3f}\ \text{{kN}}'))
    display(Math(rf'EI\,\frac{{d^2v}}{{dx^2}} = M(x) = {_equation_tex(kind, a, P, 0)}'))
    display(Math(rf'EI\,\theta = {_equation_tex(kind, a, P, 1)} + C_1'))
    display(Math(rf'EI\,v = {_equation_tex(kind, a, P, 2)} + C_1 x + C_2'))
    if kind == 'cantilever':
        bc = r'\theta(0) = 0,\ v(0) = 0'
    else:
        bc = rf'v(0) = 0,\ v({b["LB"]:g}) = 0'
    display(Math(rf'\text{{邊界條件}}\ {bc}\ \Rightarrow\ C_1 = {C1 + 0.0:.4g},\ C_2 = {C2 + 0.0:.4g}'))
    display(Math(rf'x = {probe:.2f}\ \text{{m}}:\quad \theta = {float(th_p):.5f}\ \text{{rad}},\quad '
                 rf'v = {float(v_p) * 1e3:.3f}\ \text{{mm}}'))
    tex, v_book, x_book = textbook_check(kind, a, P, EI)
    v_int = float(solve(kind, a, P, EI, x_book)[2])
    display(Math(rf'\text{{課本公式檢核：}}\ {tex} = {v_book * 1e3:.3f}\ \text{{mm}}'
                 rf'\quad(\text{{積分法}}:\ {v_int * 1e3:.3f}\ \text{{mm}})'))


# ---------------------------------------------------------------- 互動介面

def demo(kind='simple', a0=None, P=P0, EI=EI0):
    """建立互動介面：設定載重位置 a、大小 P、EI 與觀察點 x，即時更新 θ(x)、v(x)。"""
    if kind not in BEAMS:
        raise ValueError(f'kind 必須是 {list(BEAMS)} 之一')
    b = BEAMS[kind]
    L = b['L']
    a0 = b['a0'] if a0 is None else a0
    wide = widgets.Layout(width='450px')
    style = {'description_width': 'initial'}

    a_slider = widgets.FloatSlider(value=a0, min=0, max=L, step=0.1, description='載重位置 a (m)',
                                   readout_format='.1f', layout=wide, style=style)
    a_text = widgets.BoundedFloatText(value=a0, min=0, max=L, step=0.01, description='輸入 a',
                                      layout=widgets.Layout(width='180px'))
    widgets.link((a_slider, 'value'), (a_text, 'value'))
    p_slider = widgets.FloatSlider(value=b['probe0'], min=0, max=L, step=0.1,
                                   description='觀察點 x (m)', readout_format='.1f',
                                   layout=wide, style=style)
    p_text = widgets.BoundedFloatText(value=b['probe0'], min=0, max=L, step=0.01, description='輸入 x',
                                      layout=widgets.Layout(width='180px'))
    widgets.link((p_slider, 'value'), (p_text, 'value'))
    P_text = widgets.BoundedFloatText(value=P, min=0.1, max=1e4, step=1, description='P (kN)',
                                      layout=widgets.Layout(width='180px'))
    EI_text = widgets.BoundedFloatText(value=EI, min=1, max=1e9, step=1000, description='EI (kN·m²)',
                                       layout=widgets.Layout(width='240px'), style=style)
    show_curve = widgets.Checkbox(value=True, description='顯示彈性曲線')
    show_calc = widgets.Checkbox(value=True, description='顯示計算過程')
    plot_out = widgets.Output()
    calc_out = widgets.Output()

    def refresh(*_):
        a, probe = a_text.value, p_text.value
        with plot_out:
            plot_out.clear_output(wait=True)
            plot_state(kind, a, P_text.value, EI_text.value, probe, show_curve.value)
        with calc_out:
            calc_out.clear_output(wait=True)
            if show_calc.value:
                show_working(kind, a, P_text.value, EI_text.value, probe)

    for w in (a_text, p_text, P_text, EI_text, show_curve, show_calc):
        w.observe(refresh, names='value')

    controls = widgets.VBox([
        widgets.HBox([a_slider, a_text]),
        widgets.HBox([p_slider, p_text]),
        widgets.HBox([P_text, EI_text, show_curve, show_calc]),
    ])
    display(widgets.VBox([controls, plot_out, calc_out]))
    refresh()
