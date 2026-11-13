"""例題 6.1 — A 點反力影響線的互動示範。

在 notebook 中使用：
    from ex6_01 import demo
    demo()
"""
import numpy as np
import matplotlib.pyplot as plt
import ipywidgets as widgets
from IPython.display import display, Math

from cjk_font import setup_cjk_font

# 中文字型（本機用已安裝字型；Colab / Binder 會自動下載 Noto Sans TC）
setup_cjk_font()

L = 10.0                                  # 跨距 (m)
TEXTBOOK_X = (0.0, 2.5, 5.0, 7.5, 10.0)   # 課本表格 (d) 的 x 值


def Ay(x):
    return 1 - x / L


def By(x):
    return x / L


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
    """上圖：梁的自由體圖（單位載重 + 反力箭頭）。"""
    ay, by = Ay(x), By(x)
    ax.add_patch(plt.Rectangle((0, -0.08), L, 0.16, fc='#9ecae1', ec='k', zorder=2))
    _draw_support(ax, 0, 'pin')
    _draw_support(ax, L, 'roller')

    # 單位載重
    ax.annotate('', xy=(x, 0.1), xytext=(x, 1.6),
                arrowprops=dict(arrowstyle='-|>', lw=2.5, color='crimson', mutation_scale=20))
    ax.text(x + 0.15, 1.45, '1', color='crimson', fontsize=14, fontweight='bold')

    # x 尺寸線
    if x > 0.05:
        ax.annotate('', xy=(x, 2.0), xytext=(0, 2.0), arrowprops=dict(arrowstyle='<->', lw=1))
        ax.plot([0, 0], [0.2, 2.15], 'k:', lw=0.8)
    ax.text(x / 2, 2.15, f'x = {x:.2f} m', ha='center', fontsize=11)

    # 反力箭頭（長度與反力大小成比例）
    for x0, R, name in ((0, ay, r'$A_y$'), (L, by, r'$B_y$')):
        if R > 1e-9:
            ax.annotate('', xy=(x0, -0.75), xytext=(x0, -0.75 - 1.8 * R),
                        arrowprops=dict(arrowstyle='-|>', lw=2.5, color='navy', mutation_scale=18))
        ax.text(x0 + (-0.35 if x0 == 0 else 0.35), -1.2, f'{name} = {R:.3f}',
                ha='right' if x0 == 0 else 'left', fontsize=12, color='navy')

    # 跨距標示
    ax.annotate('', xy=(0, -2.9), xytext=(L, -2.9), arrowprops=dict(arrowstyle='<->', lw=1))
    ax.text(L / 2, -2.75, f'{L:g} m', ha='center', fontsize=11)
    ax.text(-0.1, 0.3, 'A', fontsize=13, ha='right')
    ax.text(L + 0.1, 0.3, 'B', fontsize=13)

    ax.set_xlim(-2.2, L + 2.2)
    ax.set_ylim(-3.2, 2.6)
    ax.set_aspect('equal')
    ax.axis('off')


def _draw_influence_line(ax, x, recorded, show_full):
    """下圖：A_y 的影響線、已記錄的點與目前位置。"""
    ay = Ay(x)
    xs = np.linspace(0, L, 200)
    if show_full:
        ax.fill_between(xs, Ay(xs), color='#c6e9fa')
        ax.plot(xs, Ay(xs), color='#1fa2e0', lw=2.5, label=r'$A_y = 1 - \frac{1}{10}x$')
    if recorded:
        xr = sorted(recorded)
        ax.plot(xr, [recorded[k] for k in xr], 'ko', ms=6, label='已記錄的點')
    ax.plot([x], [ay], 'o', color='crimson', ms=11, zorder=5, label='目前位置')
    ax.plot([x, x], [0, ay], '--', color='crimson', lw=1)
    ax.axhline(0, color='k', lw=1)

    ax.set_xlim(-0.5, L + 0.5)
    ax.set_ylim(-0.15, 1.25)
    ax.set_xticks(np.arange(0, L + 0.1, 2.5))
    ax.set_xlabel('單位載重位置 x (m)')
    ax.set_ylabel(r'$A_y$')
    ax.set_title(r'$A_y$ 的影響線')
    ax.grid(alpha=0.3)
    ax.legend(loc='upper right')


def plot_state(x, recorded=None, show_full=False):
    """畫出單位載重在 x 時的自由體圖與影響線，並列出計算式。"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6),
                                   gridspec_kw={'height_ratios': [1, 1.1]})
    _draw_beam(ax1, x)
    _draw_influence_line(ax2, x, recorded or {}, show_full)
    plt.tight_layout()
    plt.show()

    # 與課本相同格式的計算式
    display(Math(rf'\circlearrowleft +\Sigma M_B = 0:\ -A_y({L:g}) + 1\,({L - x:.2f}) = 0'
                 rf'\quad\Rightarrow\quad A_y = {Ay(x):.3f},\quad B_y = 1 - A_y = {By(x):.3f}'))


def demo(x0=2.5):
    """建立互動介面：滑桿 / 輸入框設定 x，按鈕記錄點、清除、載入課本表格。"""
    recorded = {}  # x -> Ay

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
            print(f'{"x (m)":>7} | {"A_y":>6}')
            print('-' * 16)
            for k in sorted(recorded):
                print(f'{k:7.2f} | {recorded[k]:6.3f}')

    def on_record(_):
        x = round(x_text.value, 2)
        recorded[x] = Ay(x)
        refresh()

    def on_clear(_):
        recorded.clear()
        refresh()

    def on_textbook(_):
        recorded.update({x: Ay(x) for x in TEXTBOOK_X})
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
