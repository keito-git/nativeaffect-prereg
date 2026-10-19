# 事前登録: 軸2 強度掃引実験
# 登録日時: 2026-09-25（スイープ実行前）
# 登録者: 実験担当
# 助教承認: 2026-09-25（「予測を書いてから確かめる」指示に基づく）

## 背景

v5 の結果 (Layer5, seed=42, n=10, alpha_rel=0.05) において ICA axis 2 は以下の特性を示した：
- JS比 (target/rand) = 2.67 ← 出力分布に最大の影響
- effect_diff = -0.125 ← 感情変化はランダムを下回る
- bigram繰り返し率 = 0.542（3軸中最高）
- 3人称代名詞率 = 0.050（3軸中最低）
- 上位語彙: content, grateful, angry... ← 感情語を含むが判定器が「変化」と認識しない

v5 分析からの暫定記述: 「自己参照ループ/生成安定性に関連する軸」

## 仮説

H1: axis 2 は LLM の「生成安定性/自己参照」に関する内部表現を操作している。

具体的には: この方向への摂動が「次トークンの確率を特定パターン（直前コンテキストの繰り返し）に集中させる」効果を持つ。

## 事前登録予測（確認前に登録; 実験後の変更禁止）

### P1: 繰り返し率の単調増加
alpha を [0.01, 0.03, 0.05, 0.10, 0.20] と上げたとき、
bigram 繰り返し率が単調に増加する（Spearman ρ ≥ 0.80, p < 0.05）。

方向: pos（+polarity）での測定。

### P2: 3人称代名詞率の単調減少
同じ alpha 系列で、3人称代名詞率（he/she/they等）が単調に減少する
（Spearman ρ ≤ -0.70）。

### P3: JS と alpha の単調関係
JS divergence (target vs baseline) は alpha に対して単調増加する。

### P4: 感情変化スコアは非増加
effect_diff (target - rand) は alpha に対して増加しない（≤ 0.10 for all alpha）。

## 反証条件（予測が外れた場合の対処）

- P1 が外れる（ρ < 0.80）: 「自己参照ループ」記述を棄却し「記述不能軸」と報告する。
- P2 が外れる: P1 が成立していても「人称とは無関係」と記述を修正する。
- P1 AND P2 共に外れる: 軸2の解釈は「未解明」で報告し、A-18（応答空間逆算）に委ねる。

## 実験設計

対象モデル: swiss-ai/Apertus-v1.1-1.5B
対象層: Layer 5（v5と同条件）
ICA 軸: v5 の axis 2（reproducibility score = 0.926; FastICA order 2位）
alpha_rel: [0.01, 0.03, 0.05, 0.10, 0.20] （5点）
stimuli: E4 indices 0-39（n=40）
polarity: +1 のみ（方向特定のため片側）
比較対照: rand_dir（同一刺激・同一alpha）
seed: 42
GPU: 0 のみ

解析指標:
- bigram_rep: analyze_axis_descriptions.py の repetition_rate()
- third_person_rate: person_distribution()['3rd']
- mean_js_target: run_intervention.py の js_divergence()
- effect_diff: _emotion_changed() target vs rand

検定: Spearman 相関（n=5点, alpha水準 p<0.05）

## 結果記録先（実験後に記入）

予測 | 実測 Spearman ρ | 結果（支持/棄却）
-----|-----------------|------------------
P1   | [TBD]           | [TBD]
P2   | [TBD]           | [TBD]
P3   | [TBD]           | [TBD]
P4   | [TBD]           | [TBD]


---

# 【無効】2026-09-25 追記: 本事前登録は無効

記録者: 実験担当 / 記録日: 2026-09-25 / 指示: 助教

**本事前登録は無効である。削除せず、記録として残す。**

理由: 本登録が指す「Axis 0 / Axis 1 / Axis 2」は、PAD位置の活性から推定された
ICA軸である。`extract_activations.py` が `padding=True`（`padding_side="right"`）・
`batch_size=8` でバッチ化した上で `hs[:, -1, :]` を取っていたため、バッチ内で最長でない
刺激では index −1 が PAD 位置になっていた。E1刺激300件のうち **258件（86.0%）** が
該当する（トークン長4〜47、PADオフセット平均12.59・最大40）。

診断は確定している。バグ経路を同一プロセス内で再現し、保存済み .npz と行ごとに比較した
結果、余弦 = 1.0000（4層すべて）。

修正後の活性で軸を作り直した結果、旧軸と新軸は同一とは言えない
（上位5軸をマッチング後の |cos| 平均: 層5 = 0.133、層7 = 0.145、層10 = 0.179、
層12 = 0.316。2048次元の無作為基準は約0.018）。成分数も層5で20→6、層10で18→5 と変化した。

したがって本登録の予測 P1–P4 / O1–O2 / R1–R3 / S1–S2 は、**指示対象そのものが存在しない**
ため検証不能である。「Axis 2 = 自己参照ループ/生成安定性型」等の暫定記述も、
その根拠となった生成テキスト・繰り返し率・人称率はすべて旧軸への介入によるものであり、
引き継がない。

後継: `axis_rebuilt_prereg_20260925.md`（新軸を前提に、本登録の結果を見た後に作成したことを
明記してある）

証拠ファイル:
- /path/to/work/results/axes_nopad/axis_damage_report_20260925T110342Z.json
- /path/to/work/results/logs/axis2_intensity_sweep_INVALID.json
