"""例題 6.4 — 外伸梁 C 點剪力影響線的互動示範。

在 notebook 中使用：
    from ex6_04 import demo
    demo()
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import ipywidgets as widgets
from IPython.display import display, Math

from cjk_font import setup_cjk_font

# 中文字型（本機用已安裝字型；Colab / Binder 會自動下載 Noto Sans TC）
setup_cjk_font()

LB = 8.0     # A 到 B 的距離 (m)
L = 12.0     # 梁全長 (m)，B 右側外伸 4 m
XC = 4.0     # C 點位置 (m)
# 課本表格 (d) 的點：(x, 載重在 C 的哪一側)
TEXTBOOK_PTS = ((0.0, '-'), (4.0, '-'), (4.0, '+'), (8.0, '+'), (12.0, '+'))


def Ay(x):
    return 1 - x / LB


def By(x):
    return x / LB


def at_C(x):
    return abs(x - XC) < 1e-6


def on_right(x, side='+'):
    """單位載重是否位於 C 右側的梁段 CB 上（x = 4 時由 side 決定 4⁻ / 4⁺）。"""
    return x > XC + 1e-6 or (at_C(x) and side == '+')


def VC(x, side='+'):
    # 取 C 右側段（含 B 與外伸段）自由體：+↑ΣFy = 0: V_C + B_y - (1 若載重在 CB 上) = 0
    return (1.0 if on_right(x, side) else 0.0) - By(x)


def x_label(x, side, math=False):
    # 文字表格用 Unicode 上標；圖上用 mathtext（中文字型沒有上標正負號）
    if not at_C(x):
        return f'{x:g}'
    return rf'${XC:g}^{side}$' if math else f'{XC:g}{"⁺" if side == "+" else "⁻"}'


def _draw_support(ax, x0, kind):
    # 簡單的鉸支承 (pin) / 滾支承 (roller) 符號
    ax.add_patch(plt.Polygon([[x0, 0], [x0 - 0.25, -0.45], [x0 + 0.25, -0.45]],
                             closed=True, fc='white', ec='k', lw=1.2, zorder=3))
    if kind == 'roller':
        for dx in (-0.15, 0.15):
            ax.add_patch(plt.Circle((x0 + dx, -0.55), 0.09, fc='white', ec='k', lw=1, zorder=3))
        ax.plot([x0 - 0.4, x0 + 0.4], [-0.66, -0.66], 'k', lw=1)
    else:
        ax.plot([x0 - 0.4, x0 + 0.4], [-0.46, -0.46], 'k', lw=1)


def _vertical_force(ax, x0, F, base, scale, color, label, ha, label_y=None):
    """在 x0 畫一個大小為 |F| 的垂直力：F > 0 向上（由下往上指向 base），F < 0 向下。"""
    if abs(F) > 1e-9:
        tip, tail = base, base - 0.4 - scale * abs(F)   # 0.4 = 最短箭身，避免小力只剩箭頭
        if F < 0:
            tip, tail = tail, tip
        ax.annotate('', xy=(x0, tip), xytext=(x0, tail),
                    arrowprops=dict(arrowstyle='-|>', lw=2.5, color=color, mutation_scale=18))
    dx = -0.3 if ha == 'right' else 0.3
    ax.text(x0 + dx, base - 0.45 if label_y is None else label_y, f'{label} = {F:.3f}',
            ha=ha, fontsize=11, color=color)


def _draw_load(ax, x):
    ax.annotate('', xy=(x, 0.1), xytext=(x, 1.5),
                arrowprops=dict(arrowstyle='-|>', lw=2.5, color='crimson', mutation_scale=20))
    ax.text(x + 0.15, 1.3, '1', color='crimson', fontsize=14, fontweight='bold')


def _draw_beam(ax, x, side):
    """上圖：整根梁的自由體圖。"""
    ax.add_patch(plt.Rectangle((0, -0.08), L, 0.16, fc='#9ecae1', ec='k', zorder=2))
    _draw_support(ax, 0, 'pin')
    _draw_support(ax, LB, 'roller')
    ax.plot([XC], [0], 'ko', ms=5, zorder=4)
    ax.text(XC, -0.55, 'C', ha='center', fontsize=12)

    # 載重在 C 點時稍微偏移，讓 4⁻ / 4⁺ 看得出來
    xd = x + (0.12 if side == '+' else -0.12) if at_C(x) else x
    _draw_load(ax, xd)
    if x > 0.05:
        ax.annotate('', xy=(xd, 1.9), xytext=(0, 1.9), arrowprops=dict(arrowstyle='<->', lw=1))
        ax.plot([0, 0], [0.2, 2.05], 'k:', lw=0.8)
    ax.text(xd / 2, 2.05, f'x = {x_label(x, side, math=True)} m', ha='center', fontsize=11)

    _vertical_force(ax, 0, Ay(x), -0.75, 1.2, 'navy', r'$A_y$', 'right')
    _vertical_force(ax, LB, By(x), -0.75, 1.2, 'navy', r'$B_y$', 'left')
    ax.text(-0.1, 0.3, 'A', fontsize=13, ha='right')
    ax.text(LB + 0.1, 0.3, 'B', fontsize=13)

    ax.set_xlim(-2.2, L + 2.2)
    ax.set_ylim(-3.2, 2.4)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('整體自由體圖', fontsize=11)


def _draw_segment(ax, x, side):
    """中圖：在 C 切開，取右段（含 B 與外伸段）的自由體圖。"""
    vc = VC(x, side)
    ax.add_patch(plt.Rectangle((XC, -0.08), L - XC, 0.16, fc='#9ecae1', ec='k', zorder=2))
    if on_right(x, side):
        _draw_load(ax, max(x, XC + 0.05))

    _vertical_force(ax, XC - 0.15, vc, -0.1, 1.6, 'darkgreen', r'$V_C$', 'right', label_y=-2.2)
    _vertical_force(ax, LB, By(x), -0.75, 1.2, 'navy', r'$B_y$', 'left')
    ax.text(LB - 0.1, 0.3, 'B', ha='right', fontsize=12)
    ax.add_patch(FancyArrowPatch((XC - 0.9, -0.6), (XC - 0.9, 0.7), connectionstyle='arc3,rad=-0.5',
                                 arrowstyle='-|>', mutation_scale=15, lw=1.8, color='deepskyblue'))
    ax.text(XC - 1.35, 0.5, r'$M_C$', ha='right', fontsize=11, color='deepskyblue')

    ax.set_xlim(-2.2, L + 2.2)
    ax.set_ylim(-3.2, 1.8)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(r'切開 C 點，取右段（$V_C$ 向上為正）', fontsize=11)


def _draw_influence_line(ax, x, side, recorded, show_full):
    """下圖：V_C 的影響線、已記錄的點與目前位置。"""
    vc = VC(x, side)
    if show_full:
        xl, xr = np.linspace(0, XC, 50), np.linspace(XC, L, 150)
        ax.fill_between(xl, -xl / LB, color='#c6e9fa')
        ax.fill_between(xr, 1 - xr / LB, color='#c6e9fa')
        ax.plot(xl, -xl / LB, color='#1fa2e0', lw=2.5, label=r'$V_C = -\frac{1}{8}x$')
        ax.plot(xr, 1 - xr / LB, color='#f07f1f', lw=2.5, label=r'$V_C = 1 - \frac{1}{8}x$')
        ax.plot([XC, XC], [-XC / LB, 1 - XC / LB], 'k:', lw=1)
        ax.plot([L, L], [0, 1 - L / LB], 'k:', lw=1)
        ax.text(XC + 0.1, 0.1, '跳躍量 = 1', fontsize=9)
    if recorded:
        pts = sorted(recorded.values())
        ax.plot([p[0] for p in pts], [p[1] for p in pts], 'ko', ms=6, label='已記錄的點')
    ax.plot([x], [vc], 'o', color='crimson', ms=11, zorder=5, label='目前位置')
    ax.plot([x, x], [0, vc], '--', color='crimson', lw=1)
    ax.axhline(0, color='k', lw=1)
    ax.axvline(XC, color='gray', lw=0.8, ls=':')
    ax.axvline(LB, color='gray', lw=0.8, ls=':')
    ax.text(LB + 0.1, -0.7, '支承 B', color='gray', fontsize=9)

    ax.set_xlim(-0.5, L + 0.5)
    ax.set_ylim(-0.75, 0.9)
    ax.set_xticks(np.arange(0, L + 0.1, 2))
    ax.set_xlabel('單位載重位置 x (m)')
    ax.set_ylabel(r'$V_C$')
    ax.set_title(r'$V_C$ 的影響線', fontsize=11)
    ax.grid(alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)


def plot_state(x, side='+', recorded=None, show_full=False):
    """畫出單位載重在 x 時的整體 / 右段自由體圖與 V_C 影響線，並列出計算式。"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7, 8),
                                        gridspec_kw={'height_ratios': [1, 0.9, 1.1]})
    _draw_beam(ax1, x, side)
    _draw_segment(ax2, x, side)
    _draw_influence_line(ax3, x, side, recorded or {}, show_full)
    plt.tight_layout()
    plt.show()

    # 與課本相同格式的計算式
    load = '- 1' if on_right(x, side) else ''
    display(Math(rf'\circlearrowleft +\Sigma M_A = 0:\ B_y({L:g}) - 1\,({x:.2f}) = 0'
                 rf'\quad\Rightarrow\quad B_y = {By(x):.3f}'))
    display(Math(rf'\text{{C 右段}}:\ +\uparrow\Sigma F_y = 0:\ V_C + {By(x):.3f} {load} = 0'
                 rf'\quad\Rightarrow\quad V_C = {VC(x, side):.3f}'))


def demo(x0=4.0):
    """建立互動介面：滑桿 / 輸入框設定 x，x = 4 時可選 4⁻ / 4⁺；按鈕記錄點、清除、載入課本表格。"""
    recorded = {}  # (x, side) -> (x, V_C)

    x_slider = widgets.FloatSlider(value=x0, min=0, max=L, step=0.1, description='x (m)',
                                   readout_format='.1f', layout=widgets.Layout(width='450px'))
    x_text = widgets.BoundedFloatText(value=x0, min=0, max=L, step=0.01, description='輸入 x',
                                      layout=widgets.Layout(width='180px'))
    widgets.link((x_slider, 'value'), (x_text, 'value'))
    side = widgets.ToggleButtons(options=[('C 左側 4⁻', '-'), ('C 右側 4⁺', '+')], value='-',
                                 description='x = 4 時', style={'button_width': '110px'})

    show_full = widgets.Checkbox(value=False, description='顯示完整影響線')
    btn_record = widgets.Button(description='記錄此點', button_style='primary', icon='plus')
    btn_clear = widgets.Button(description='清除記錄', icon='trash')
    btn_textbook = widgets.Button(description='載入課本表格點', icon='table')
    plot_out = widgets.Output()
    table_out = widgets.Output()

    def refresh(*_):
        side.disabled = not at_C(x_text.value)
        with plot_out:
            plot_out.clear_output(wait=True)
            plot_state(x_text.value, side.value, recorded, show_full.value)
        with table_out:
            table_out.clear_output()
            if not recorded:
                print('（尚未記錄任何點）')
                return
            print(f'{"x (m)":>7} | {"V_C":>6}')
            print('-' * 16)
            for (xk, s), (_, v) in sorted(recorded.items(), key=lambda kv: (kv[0][0], kv[0][1] == '+')):
                print(f'{x_label(xk, s):>7} | {v:6.3f}')

    def record(x, s):
        x = round(x, 2)
        s = s if at_C(x) else '+'
        recorded[(x, s)] = (x, VC(x, s))

    def on_record(_):
        record(x_text.value, side.value)
        refresh()

    def on_clear(_):
        recorded.clear()
        refresh()

    def on_textbook(_):
        for x, s in TEXTBOOK_PTS:
            record(x, s)
        refresh()

    for w in (x_text, side, show_full):
        w.observe(refresh, names='value')
    btn_record.on_click(on_record)
    btn_clear.on_click(on_clear)
    btn_textbook.on_click(on_textbook)

    controls = widgets.VBox([
        widgets.HBox([x_slider, x_text]),
        side,
        widgets.HBox([btn_record, btn_clear, btn_textbook, show_full]),
    ])
    table = widgets.VBox([widgets.HTML('<b>記錄表</b>'), table_out],
                         layout=widgets.Layout(margin='0 0 0 20px'))
    display(widgets.HBox([widgets.VBox([controls, plot_out]), table]))
    refresh()
