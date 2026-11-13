"""例題 6.2 — 外伸梁 B 點反力影響線的互動示範。

在 notebook 中使用：
    from ex6_02 import demo
    demo()
"""
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, Math

# 中文字型（Windows: 微軟正黑體；其他系統自動退回）
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Noto Sans CJK TC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

LB = 5.0                                  # A 到 B 的距離 (m)
L = 10.0                                  # 梁全長 (m)，B 右側外伸 5 m
TEXTBOOK_X = (0.0, 2.5, 5.0, 7.5, 10.0)   # 課本表格 (b) 的 x 值


def By(x):
    return x / LB


def Ay(x):
    return 1 - x / LB


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


def _draw_beam(ax, x):
    """上圖：外伸梁的自由體圖（單位載重 + 反力箭頭）。"""
    ax.add_patch(plt.Rectangle((0, -0.08), L, 0.16, fc='#9ecae1', ec='k', zorder=2))
    _draw_support(ax, 0, 'pin')
    _draw_support(ax, LB, 'roller')

    # 單位載重
    ax.annotate('', xy=(x, 0.1), xytext=(x, 1.6),
                arrowprops=dict(arrowstyle='-|>', lw=2.5, color='crimson', mutation_scale=20))
    ax.text(x + 0.15, 1.45, '1', color='crimson', fontsize=14, fontweight='bold')

    # x 尺寸線
    if x > 0.05:
        ax.annotate('', xy=(x, 2.0), xytext=(0, 2.0), arrowprops=dict(arrowstyle='<->', lw=1))
        ax.plot([0, 0], [0.2, 2.15], 'k:', lw=0.8)
    ax.text(x / 2, 2.15, f'x = {x:.2f} m', ha='center', fontsize=11)

    # 反力箭頭（長度與反力大小成比例；負值 = 向下）
    for x0, R, name, side in ((0, Ay(x), r'$A_y$', -1), (LB, By(x), r'$B_y$', 1)):
        if abs(R) > 1e-9:
            tip, tail = -0.75, -0.75 - 1.0 * abs(R)
            if R < 0:
                tip, tail = tail, tip
            ax.annotate('', xy=(x0, tip), xytext=(x0, tail),
                        arrowprops=dict(arrowstyle='-|>', lw=2.5, color='navy', mutation_scale=18))
        ax.text(x0 + 0.35 * side, -1.2, f'{name} = {R:.3f}',
                ha='left' if side > 0 else 'right', fontsize=12, color='navy')

    # 尺寸標示：A–B 5 m、外伸 5 m
    for x1, x2 in ((0, LB), (LB, L)):
        ax.annotate('', xy=(x1, -3.0), xytext=(x2, -3.0), arrowprops=dict(arrowstyle='<->', lw=1))
        ax.text((x1 + x2) / 2, -2.85, f'{x2 - x1:g} m', ha='center', fontsize=11)
    ax.text(-0.1, 0.3, 'A', fontsize=13, ha='right')
    ax.text(LB + 0.1, 0.3, 'B', fontsize=13)

    ax.set_xlim(-2.2, L + 1.0)
    ax.set_ylim(-3.3, 2.6)
    ax.set_aspect('equal')
    ax.axis('off')


def _draw_influence_line(ax, x, recorded, show_full):
    """下圖：B_y 的影響線、已記錄的點與目前位置。"""
    by = By(x)
    xs = np.linspace(0, L, 200)
    if show_full:
        ax.fill_between(xs, By(xs), color='#c6e9fa')
        ax.plot(xs, By(xs), color='#1fa2e0', lw=2.5, label=r'$B_y = \frac{1}{5}x$')
    if recorded:
        xr = sorted(recorded)
        ax.plot(xr, [recorded[k] for k in xr], 'ko', ms=6, label='已記錄的點')
    ax.plot([x], [by], 'o', color='crimson', ms=11, zorder=5, label='目前位置')
    ax.plot([x, x], [0, by], '--', color='crimson', lw=1)
    ax.axhline(0, color='k', lw=1)
    ax.axhline(1, color='gray', lw=0.8, ls=':')
    ax.axvline(LB, color='gray', lw=0.8, ls=':')
    ax.text(LB + 0.1, 2.25, '支承 B', color='gray', fontsize=9)

    ax.set_xlim(-0.5, L + 0.5)
    ax.set_ylim(-0.2, 2.4)
    ax.set_xticks(np.arange(0, L + 0.1, 2.5))
    ax.set_xlabel('單位載重位置 x (m)')
    ax.set_ylabel(r'$B_y$')
    ax.set_title(r'$B_y$ 的影響線')
    ax.grid(alpha=0.3)
    ax.legend(loc='upper left')


def plot_state(x, recorded=None, show_full=False):
    """畫出單位載重在 x 時的自由體圖與影響線，並列出計算式。"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6),
                                   gridspec_kw={'height_ratios': [1, 1.1]})
    _draw_beam(ax1, x)
    _draw_influence_line(ax2, x, recorded or {}, show_full)
    plt.tight_layout()
    plt.show()

    # 與課本相同格式的計算式
    display(Math(rf'\circlearrowleft +\Sigma M_A = 0:\ B_y({LB:g}) - 1\,({x:.2f}) = 0'
                 rf'\quad\Rightarrow\quad B_y = {By(x):.3f},\quad A_y = 1 - B_y = {Ay(x):.3f}'))


def demo(x0=2.5):
    """建立互動介面：滑桿 / 輸入框設定 x，按鈕記錄點、清除、載入課本表格。"""
    recorded = {}  # x -> By

    x_slider = widgets.FloatSlider(value=x0, min=0, max=L, step=0.1, description='x (m)',
                                   readout_format='.1f', layout=widgets.Layout(width='450px'))
    x_text = widgets.BoundedFloatText(value=x0, min=0, max=L, step=0.01, description='輸入 x',
                                      layout=widgets.Layout(width='180px'))
    widgets.link((x_slider, 'value'), (x_text, 'value'))

    show_full = widgets.Checkbox(value=False, description='顯示完整影響線')
    btn_record = widgets.Button(description='記錄此點', button_style='primary', icon='plus')
    btn_clear = widgets.Button(description='清除記錄', icon='trash')
    btn_textbook = widgets.Button(description='載入課本表格點', icon='table')
    plot_out = widgets.Output()
    table_out = widgets.Output()

    def refresh(*_):
        with plot_out:
            plot_out.clear_output(wait=True)
            plot_state(x_text.value, recorded, show_full.value)
        with table_out:
            table_out.clear_output()
            if not recorded:
                print('（尚未記錄任何點）')
                return
            print(f'{"x (m)":>7} | {"B_y":>6}')
            print('-' * 16)
            for k in sorted(recorded):
                print(f'{k:7.2f} | {recorded[k]:6.3f}')

    def on_record(_):
        x = round(x_text.value, 2)
        recorded[x] = By(x)
        refresh()

    def on_clear(_):
        recorded.clear()
        refresh()

    def on_textbook(_):
        recorded.update({x: By(x) for x in TEXTBOOK_X})
        refresh()

    x_text.observe(refresh, names='value')
    show_full.observe(refresh, names='value')
    btn_record.on_click(on_record)
    btn_clear.on_click(on_clear)
    btn_textbook.on_click(on_textbook)

    controls = widgets.VBox([
        widgets.HBox([x_slider, x_text]),
        widgets.HBox([btn_record, btn_clear, btn_textbook, show_full]),
    ])
    table = widgets.VBox([widgets.HTML('<b>記錄表</b>'), table_out],
                         layout=widgets.Layout(margin='0 0 0 20px'))
    display(widgets.HBox([widgets.VBox([controls, plot_out]), table]))
    refresh()
