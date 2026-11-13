# Structural analysis: influence lines for statically determinate beams

Interactive Jupyter notebooks that build the influence lines of support reactions, shear and
bending moment for simply supported and overhanging beams. A unit load is moved along the
beam, and each position is recorded point by point to trace the influence line, which can then
be compared with the theoretical result from statics. The notebooks are written in Traditional Chinese.

## Notebooks

| Notebook | Example | Quantity | Beam | Colab | Binder |
| --- | --- | --- | --- | --- | --- |
| [ex6-01_influence_line_Ay.ipynb](influenceline/ex6-01_influence_line_Ay.ipynb) | 6.1 | Support reaction $A_y$ | Simply supported, $L = 10$ m | <a href="https://colab.research.google.com/github/AaronOET/ntouoet_structure_analysis_1151/blob/main/influenceline/ex6-01_influence_line_Ay.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> | <a href="https://mybinder.org/v2/gh/AaronOET/ntouoet_structure_analysis_1151/main?labpath=influenceline/ex6-01_influence_line_Ay.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://mybinder.org/badge_logo.svg" alt="Binder"></a> |
| [ex6-02_influence_line_By.ipynb](influenceline/ex6-02_influence_line_By.ipynb) | 6.2 | Support reaction $B_y$ | Overhanging, $AB = 5$ m + 5 m overhang | <a href="https://colab.research.google.com/github/AaronOET/ntouoet_structure_analysis_1151/blob/main/influenceline/ex6-02_influence_line_By.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> | <a href="https://mybinder.org/v2/gh/AaronOET/ntouoet_structure_analysis_1151/main?labpath=influenceline/ex6-02_influence_line_By.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://mybinder.org/badge_logo.svg" alt="Binder"></a> |
| [ex6-03_influence_line_Vc.ipynb](influenceline/ex6-03_influence_line_Vc.ipynb) | 6.3 | Shear $V_C$ | Simply supported, $L = 10$ m, $C$ at 2.5 m | <a href="https://colab.research.google.com/github/AaronOET/ntouoet_structure_analysis_1151/blob/main/influenceline/ex6-03_influence_line_Vc.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> | <a href="https://mybinder.org/v2/gh/AaronOET/ntouoet_structure_analysis_1151/main?labpath=influenceline/ex6-03_influence_line_Vc.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://mybinder.org/badge_logo.svg" alt="Binder"></a> |
| [ex6-04_influence_line_Vc_overhang.ipynb](influenceline/ex6-04_influence_line_Vc_overhang.ipynb) | 6.4 | Shear $V_C$ | Overhanging, $AB = 8$ m + 4 m overhang, $C$ at 4 m | <a href="https://colab.research.google.com/github/AaronOET/ntouoet_structure_analysis_1151/blob/main/influenceline/ex6-04_influence_line_Vc_overhang.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> | <a href="https://mybinder.org/v2/gh/AaronOET/ntouoet_structure_analysis_1151/main?labpath=influenceline/ex6-04_influence_line_Vc_overhang.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://mybinder.org/badge_logo.svg" alt="Binder"></a> |
| [ex6-05_influence_line_Mc.ipynb](influenceline/ex6-05_influence_line_Mc.ipynb) | 6.5 | Moment $M_C$ | Simply supported, $L = 10$ m, $C$ at 5 m | <a href="https://colab.research.google.com/github/AaronOET/ntouoet_structure_analysis_1151/blob/main/influenceline/ex6-05_influence_line_Mc.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> | <a href="https://mybinder.org/v2/gh/AaronOET/ntouoet_structure_analysis_1151/main?labpath=influenceline/ex6-05_influence_line_Mc.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://mybinder.org/badge_logo.svg" alt="Binder"></a> |
| [ex6-06_influence_line_Mc_overhang.ipynb](influenceline/ex6-06_influence_line_Mc_overhang.ipynb) | 6.6 | Moment $M_C$ | Overhanging, $AB = 8$ m + 4 m overhang, $C$ at 4 m | <a href="https://colab.research.google.com/github/AaronOET/ntouoet_structure_analysis_1151/blob/main/influenceline/ex6-06_influence_line_Mc_overhang.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> | <a href="https://mybinder.org/v2/gh/AaronOET/ntouoet_structure_analysis_1151/main?labpath=influenceline/ex6-06_influence_line_Mc_overhang.ipynb" target="_blank" rel="noopener noreferrer"><img src="https://mybinder.org/badge_logo.svg" alt="Binder"></a> |

Each notebook derives the influence-line equation from equilibrium (and the method of sections
for $V_C$ and $M_C$), then calls `demo()`, which gives:

- a slider / text box for the unit-load position $x$,
- a **記錄此點** (record point) button that adds $(x, 	ext{value})$ to a table and the plot,
- a **顯示完整影響線** (show full influence line) checkbox to overlay the theoretical line,
- for $V_C$, a 左側/右側 switch for the load just left or right of $C$, where the shear jumps,
- for $M_C$, an adjustable position $a$ of point $C$ to check the peak value $ab/L$.

The notebooks end with questions for discussion.

## Modules

- [ex6_01.py](influenceline/ex6_01.py): `demo()` for Example 6.1
- [ex6_02.py](influenceline/ex6_02.py): `demo()` for Example 6.2
- [ex6_03.py](influenceline/ex6_03.py): `demo()` for Example 6.3
- [ex6_04.py](influenceline/ex6_04.py): `demo()` for Example 6.4
- [ex6_05.py](influenceline/ex6_05.py): `demo()` for Example 6.5
- [ex6_06.py](influenceline/ex6_06.py): `demo()` for Example 6.6

## Running locally

```bash
pip install -r requirements.txt
jupyter lab
```

Plot labels use a Chinese font (Microsoft JhengHei or Noto Sans CJK TC). If neither is
installed, as on Colab and Binder, the Chinese characters in the figures may not display.
