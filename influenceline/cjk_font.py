"""讓 matplotlib 能顯示繁體中文。

本機若已有中文字型（微軟正黑體、Noto Sans CJK TC 等）就直接使用；
否則（例如 Colab、Binder）自動下載 Noto Sans TC 並註冊給 matplotlib。

    from cjk_font import setup_cjk_font
    setup_cjk_font()
"""
import os
import urllib.request
import warnings

import matplotlib.pyplot as plt
from matplotlib import font_manager

# 依序嘗試的已安裝中文字型
INSTALLED_FONTS = ['Microsoft JhengHei', 'Noto Sans CJK TC', 'PingFang TC',
                   'Heiti TC']

# 備用：Noto Sans TC Regular（SIL Open Font License，約 5.7 MB）
FONT_URL = ('https://github.com/notofonts/noto-cjk/raw/main/'
            'Sans/SubsetOTF/TC/NotoSansTC-Regular.otf')
FONT_NAME = 'Noto Sans TC'
FONT_FILE = os.path.join(os.path.expanduser('~'), '.cache', 'cjk_font',
                         'NotoSansTC-Regular.otf')

_done = False


def _use(name):
    plt.rcParams['font.sans-serif'] = [name, 'DejaVu Sans']
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['axes.unicode_minus'] = False


def setup_cjk_font():
    """設定中文字型；回傳使用的字型名稱（找不到時回傳 None）。"""
    global _done
    if _done:
        return plt.rcParams['font.sans-serif'][0]

    available = {f.name for f in font_manager.fontManager.ttflist}
    for name in INSTALLED_FONTS:
        if name in available:
            _use(name)
            _done = True
            return name

    try:
        if not os.path.exists(FONT_FILE):
            os.makedirs(os.path.dirname(FONT_FILE), exist_ok=True)
            print('下載中文字型 Noto Sans TC ...')
            urllib.request.urlretrieve(FONT_URL, FONT_FILE + '.part')
            os.replace(FONT_FILE + '.part', FONT_FILE)
        font_manager.fontManager.addfont(FONT_FILE)
    except Exception as exc:  # 離線等情況：仍可執行，只是中文顯示為方框
        warnings.warn(f'無法取得中文字型，圖中的中文可能無法顯示：{exc}')
        plt.rcParams['axes.unicode_minus'] = False
        return None

    _use(FONT_NAME)
    _done = True
    return FONT_NAME
