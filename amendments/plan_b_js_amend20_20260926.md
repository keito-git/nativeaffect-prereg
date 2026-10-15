# 事前登録 追記20：Braun et al. の全文確認。主張②は独立。先行研究2本が互いに対立している

**対象**: 追記14 N7（先行性の確認義務）、追記15 O2（主張②の判定）
**作成**: 野村 / 2026-09-26
**状態**: **G1 の判定統計量は未計算**
**典拠**: arXiv:2505.22637 の PDF 全文（野村が取得して直接読んだ）

---

## T1. 書誌

**Joschka Braun, Carsten Eickhoff, David Krueger, Seyed Ali Bahrainian, Dmitrii Krasheninnikov (2025). Understanding (Un)Reliability of Steering Vectors in Language Models.** arXiv:2505.22637。**ICLR 2025 Workshop on Foundation Models in the Wild で発表。**

**査読の水準はワークショップである。** 本会議論文ではない。Related Work で引用する際に明記する。

## T2. 彼らの量（原文から）

$$d' = \frac{\mu_+ - \mu_-}{\sqrt{\tfrac{1}{2}(\sigma_+^2 + \sigma_-^2)}}$$

> where $\mu_+$ and $\mu_-$ are the means of the positive and negative activations **projected onto the difference-of-means line**, and $\sigma_+^2$ and $\sigma_-^2$ are their respective **variances along this line**. A higher $d'$ indicates better separation.

主張:

> Both directional agreement, as measured by cosine similarity and separability of activations, as measured by the discriminability index $d'$, are correlated with each other and are both **predictive of a larger steering effect size** and lower fraction of anti-steerable samples.

## T3. 判定：主張②は**独立**（全文確認済み）

**別の量である。**

| | Braun et al. | 我々の主張② |
|---|---|---|
| 測る対象 | **2クラスの活性が、1本の方向（差分平均線）上でどれだけ分離しているか** | **ステアリング方向が、共分散の固有基底のどこに乗っているか** |
| 分散の意味 | **クラス内分散**（射影後の各クラスの分散） | **活性雲の共分散固有構造**（上位10主成分への射影長） |
| 次元 | **1次元**（差分平均線1本） | **10次元**（上位10主成分への射影長ベクトル） |
| 主張の向き | $d'$ が高い → 効果が大きい（**順方向**） | 射影長だけで JS が予測できるか（**予測可能性そのもの**） |
| ホールドアウト $R^2$ | **報告なし** | 報告する |

**したがって主張②は独立である。** 追記15 O2 の判定は全文確認で裏付けられた。

**ただし引用は必要である。** 「介入効果が方向の意味内容ではなく幾何的な量で説明されうる」という問題意識の先例として、Related Work に置く。**「我々が最初に指摘した」と書かない。**

## T4. 発見：先行研究2本が互いに対立している

**Braun et al.（ICLR 2025 Workshop）**: クラス分離度 $d'$ は操縦効果を**予測する**。

**CRH（Gao et al., ICML 2026）**: 分離度の推定値は操縦結果と**よく相関しない**。

> "these estimates do not always correlate well with actual steering outcomes"

**両者は同じ族の量（Fisher 的クラス分離度）について逆のことを述べている。** 伊藤が CRH の separability を「Fisher 的クラス間距離 $d'$」と同定していたが、**それが Braun et al. の $d'$ と同じ量であることが、今回の全文確認で確定した。**

**この対立は我々に有利である。書き方を確定する。**

> クラス分離度が操縦可能性を予測するかについて、先行研究は一致していない（Braun et al. 2025 は予測すると報告し、Gao et al. 2026 は相関しないと報告する）。**本研究が測るのは第三の量、すなわち共分散の固有構造における方向の位置であり、この対立のいずれの側にも属さない。**

**過剰主張を防ぐ制約**:
- **どちらが正しいかを我々は判定しない。** 両者はモデル・行動・成果指標が異なる
- **「先行研究が混乱している」と書かない。** 「一致していない」までにとどめる
- **我々の量が優れていると書かない。** 別の量であると書く

## T5. 追記14 N7 の義務を完了する

N7 は3点の照会を義務づけた。**全て完了した。**

| 照会項目 | 判定 | 根拠 |
|---|---|---|
| ①「$J$ の上位特異方向と主成分の一致による同定不能性」 | **部分重複**（前半が既出） | 追記15 O1（Gao et al. 2608.22985 全文） |
| ② 分散プロファイルからの効果量の定量 | **独立**（全文確認） | 本追記 |
| ③ 効果が幾何的量で説明される研究全般 | **独立**（周辺に関連研究あり） | 追記15 O2＋本追記 |

**①は主張しない**（追記15 で取り下げ済み。予測P も外れた）。**②③は「我々の知る限り」を付けて書く。**
