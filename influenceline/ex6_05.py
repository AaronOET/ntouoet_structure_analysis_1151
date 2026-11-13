"""例題 6.5 — 簡支梁 C 點彎矩影響線的互動示範。

在 notebook 中使用：
    from ex6_05 import demo
    demo()
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
import ipywidgets as widgets
from IPython.display import display, Math

# 中文字型（Windows: 微軟正黑體；其他系統自動退回）
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Noto Sans CJK TC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

L = 10.0                                  # 跨距 (m)
XC0 = 5.0                                 # 課本 C 點位置 (m)
TEXTBOOK_X = (0.0, 2.5, 5.0, 7.5, 10.0)   # 課本表格 (c) 的 x 值


def Ay(x):
    return 1 - x / L


def By(x):
    return x / L


def on_right(x, xc):
    """單位載重是否位於 C 右側的梁段 CB 上（彎矩連續，x = a 時兩側結果相同）。"""
    return x > xc + 1e-9


def MC(x, xc=XC0):
    # 取 CB 段自由體：↺+ΣM_C = 0: -M_C + B_y (L - a) - 1·(x - a) [若載重在 CB 上] = 0
    return By(x) * (L - xc) - (x - xc if on_right(x, xc) else 0.0)


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


def _dimension(ax, x1, x2, y, text):
    if x2 - x1 > 0.05:
        ax.annotate('', xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle='<->', lw=1))
    ax.text((x1 + x2) / 2, y + 0.12, text, ha='center', fontsize=10)


def _draw_beam(ax, x, xc):
    """上圖：整根梁的自由體圖。"""
    ax.add_patch(plt.Rectangle((0, -0.08), L, 0.16, fc='#9ecae1', ec='k', zorder=2))
    _draw_support(ax, 0, 'pin')
    _draw_support(ax, L, 'roller')
    ax.plot([xc], [0], 'ko', ms=5, zorder=4)
    ax.text(xc, -0.55, 'C', ha='center', fontsize=12)

    _draw_load(ax, x)
    if x > 0.05:
        ax.plot([0, 0], [0.2, 2.05], 'k:', lw=0.8)
    _dimension(ax, 0, x, 1.9, f'x = {x:g} m')

    _vertical_force(ax, 0, Ay(x), -0.75, 1.6, 'navy', r'$A_y$', 'right')
    _vertical_force(ax, L, By(x), -0.75, 1.6, 'navy', r'$B_y$', 'left')
    ax.text(-0.1, 0.3, 'A', fontsize=13, ha='right')
    ax.text(L + 0.1, 0.3, 'B', fontsize=13)

    ax.set_xlim(-2.2, L + 2.2)
    ax.set_ylim(-2.8, 2.4)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title('整體自由體圖', fontsize=11)


def _draw_segment(ax, x, xc):
    """中圖：在 C 切開，取右段 CB 的自由體圖。"""
    mc = MC(x, xc)
    ax.add_patch(plt.Rectangle((xc, -0.08), L - xc, 0.16, fc='#9ecae1', ec='k', zorder=2))
    if on_right(x, xc):
        _draw_load(ax, x)
        _dimension(ax, xc, x, 1.75, f'{x - xc:g} m')

    # M_C：作用在右段左端面，逆時針為正（與課本相同）
    ax.add_patch(FancyArrowPatch((xc - 0.5, -0.6), (xc - 0.5, 0.7), connectionstyle='arc3,rad=-0.5',
                                 arrowstyle='-|>', mutation_scale=15, lw=2.2, color='deepskyblue'))
    ax.text(xc - 1.0, 0.6, rf'$M_C$ = {mc:.3f}', ha='right', fontsize=11, color='deepskyblue')
    ax.annotate('', xy=(xc - 0.12, 0.6), xytext=(xc - 0.12, -0.6),
                arrowprops=dict(arrowstyle='-|>', lw=1.5, color='gray'))
    ax.text(xc - 0.25, -0.95, r'$V_C$', ha='right', fontsize=10, color='gray')

    _vertical_force(ax, L, By(x), -0.75, 1.6, 'navy', r'$B_y$', 'left')
    _dimension(ax, xc, L, -2.5, f'{L - xc:g} m')

    ax.set_xlim(-2.2, L + 2.2)
    ax.set_ylim(-2.8, 2.2)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(r'切開 C 點，取右段 CB（$M_C$ 逆時針為正）', fontsize=11)


def _draw_influence_line(ax, x, xc, recorded, show_full):
    """下圖：M_C 的影響線、已記錄的點與目前位置。"""
    mc = MC(x, xc)
    peak = xc * (L - xc) / L
    if show_full:
        xs = np.array([0, xc, L])
        ms = np.array([0, peak, 0])
        ax.fill_between(xs, ms, color='#c6e9fa')
        f = lambda v: f'{v:g}'
        ax.plot(xs[:2], ms[:2], color='#1fa2e0', lw=2.5,
                label=rf'$M_C = {f((L - xc) / L)}\,x$')
        ax.plot(xs[1:], ms[1:], color='#f07f1f', lw=2.5,
                label=rf'$M_C = {f(xc)} - {f(xc / L)}\,x$')
        ax.text(xc, peak + 0.1, rf'$\frac{{ab}}{{L}} = \frac{{{f(xc)}\times{f(L - xc)}}}{{{f(L)}}} = {peak:g}$',
                ha='center', va='bottom', fontsize=11)
    if recorded:
        pts = sorted(recorded.items())
        ax.plot([p[0] for p in pts], [p[1] for p in pts], 'ko', ms=6, label='已記錄的點')
    ax.plot([x], [mc], 'o', color='crimson', ms=11, zorder=5, label='目前位置')
    ax.plot([x, x], [0, mc], '--', color='crimson', lw=1)
    ax.axhline(0, color='k', lw=1)
    ax.axvline(xc, color='gray', lw=0.8, ls=':')

    ax.set_xlim(-0.5, L + 0.5)
    ax.set_ylim(-0.3, 3.4)
    ax.set_xticks(np.arange(0, L + 0.1, 2.5))
    ax.set_xlabel('單位載重位置 x (m)')
    ax.set_ylabel(r'$M_C$ (m)')
    ax.set_title(r'$M_C$ 的影響線', fontsize=11)
    ax.grid(alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)


def plot_state(x, xc=XC0, recorded=None, show_full=False):
    """畫出單位載重在 x 時的整體 / 右段自由體圖與 M_C 影響線，並列出計算式。"""
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(7, 8.5),
                                        gridspec_kw={'height_ratios': [1, 1, 1.2]})
    _draw_beam(ax1, x, xc)
    _draw_segment(ax2, x, xc)
    _draw_influence_line(ax3, x, xc, recorded or {}, show_full)
    plt.tight_layout()
    plt.show()

    # 與課本相同格式的計算式
    load = rf' - 1\,({x - xc:.2f})' if on_right(x, xc) else ''
    display(Math(rf'\circlearrowleft +\Sigma M_A = 0:\ B_y({L:g}) - 1\,({x:.2f}) = 0'
                 rf'\quad\Rightarrow\quad B_y = {By(x):.3f}'))
    display(Math(rf'\text{{CB 段}}:\ \circlearrowleft +\Sigma M_C = 0:\ -M_C + {By(x):.3f}\,({L - xc:g}){load} = 0'
                 rf'\quad\Rightarrow\quad M_C = {MC(x, xc):.3f}'))


def demo(x0=2.5):
    """建立互動介面：滑桿 / 輸入框設定 x、C 點位置 a；按鈕記錄點、清除、載入課本表格。"""
    recorded = {}  # x -> M_C（C 點位置改變時清除）

    x_slider = widgets.FloatSlider(value=x0, min=0, max=L, step=0.1, description='x (m)',
                                   readout_format='.1f', layout=widgets.Layout(width='450px'))
    x_text = widgets.BoundedFloatText(value=x0, min=0, max=L, step=0.01, description='輸入 x',
                                      layout=widgets.Layout(width='180px'))
    widgets.link((x_slider, 'value'), (x_text, 'value'))
    a_slider = widgets.FloatSlider(value=XC0, min=1, max=L - 1, step=0.5, description='C 點 a (m)',
                                   readout_format='.1f', layout=widgets.Layout(width='450px'),
                                   style={'description_width': 'initial'})

    show_full = widgets.Checkbox(value=False, description='顯示完整影響線')
    btn_record = widgets.Button(description='記錄此點', button_style='primary', icon='plus')
    btn_clear = widgets.Button(description='清除記錄', icon='trash')
    btn_textbook = widgets.Button(description='載入課本表格點', icon='table')
    plot_out = widgets.Output()
    table_out = widgets.Output()

    def refresh(*_):
        with plot_out:
            plot_out.clear_output(wait=True)
            plot_state(x_text.value, a_slider.value, recorded, show_full.value)
        with table_out:
            table_out.clear_output()
            if not recorded:
                print('（尚未記錄任何點）')
                return
            print(f'{"x (m)":>7} | {"M_C":>6}')
            print('-' * 16)
            for xk, v in sorted(recorded.items()):
                print(f'{xk:>7g} | {v:6.3f}')

    def on_a_change(_):
        recorded.clear()   # 舊的點屬於另一個 C 位置，不再適用
        refresh()

    def on_record(_):
        x = round(x_text.value, 2)
        recorded[x] = MC(x, a_slider.value)
        refresh()

    def on_clear(_):
        recorded.clear()
        refresh()

    def on_textbook(_):
        a_slider.unobserve(on_a_change, names='value')
        a_slider.value = XC0
        a_slider.observe(on_a_change, names='value')
        recorded.clear()
        recorded.update({x: MC(x, XC0) for x in TEXTBOOK_X})
        refresh()

    for w in (x_text, show_full):
        w.observe(refresh, names='value')
    a_slider.observe(on_a_change, names='value')
    btn_record.on_click(on_record)
    btn_clear.on_click(on_clear)
    btn_textbook.on_click(on_textbook)

    controls = widgets.VBox([
        widgets.HBox([x_slider, x_text]),
        a_slider,
        widgets.HBox([btn_record, btn_clear, btn_textbook, show_full]),
    ])
    table = widgets.VBox([widgets.HTML('<b>記錄表</b>'), table_out],
                         layout=widgets.Layout(margin='0 0 0 20px'))
    display(widgets.HBox([widgets.VBox([controls, plot_out]), table]))
    refresh()
