# Fig. 1 仕様（実験担当 → 図表担当）: 測定の流れのみ

**方針（助教確定）**: **測定の流れだけを描く。主張の構造は描かない。**
条件が何個あるか・何が示されたかは Discussion に依存し、PI の枠組み判断待ちのため、
描き込むと判断後に作り直しになる。**枠組みに依存しない測定の流れだけなら今作っても無駄にならない。**

- モデル: **gpt-image-2**（ラボ標準・PI指示）。`quality=high`、横長パイプラインなので 1536x1024
- **フォントは指定しない**（反映されず崩れ要因になるため。統一は PI 最終調整）
- ベクター（matplotlib）では作らない
- 参考図フォルダ `/path/to/research/研究論文図参考/` を必ず参照してから設計
- 最大10回反復。生成プロンプトは本フォルダに保存

## 描くもの（左から右への測定フロー、5段）

1. **刺激**: 2種類を分けて描く
   - E1（287 sentences, naturalistic）→ 整合の推定に使う
   - E4（40 stimuli, 20 categories x 2 template variants;
     10 positive categories / 10 negative categories）→ 介入に使う。
     **discovery 20 / confirmation 20 に分割されることを明示**
2. **活性抽出**: decoder layers 5 / 7 / 10 / 12 の **last-token hidden state**（2048-dim）
3. **方向の構成**: この段が図の中心。**3系統が並列**であることを示す
   - **ICA axes**（E1 活性から。top-3 by split-half reproducibility）
   - **Human direction**（E1 の valence/arousal/dominance から ridge 回帰で推定）
   - **Controls（3種の床）** ← **最重要。下記 §床の描き分け**
4. **介入**: 最終トークンに `h + alpha * d` を加算（両極性）。alpha は刺激ごとに `||h_i||` で正規化
5. **測定**: 次トークン分布の **JS divergence**（介入なしとの比較、top-100 union）
   → paired Wilcoxon / bootstrap CI / Cliff's delta / BH

## 床の描き分け（**この図の中心概念。ここが伝わるかで読者の理解が決まる**）

**2048次元空間を1つの大きな楕円（または球）として描き、その中に「上位10主成分が張る
部分空間」を小さな平面（または扁平な円盤）として描く。** そのうえで3種の床を、
**どこから引かれるかが一目で分かるように**描く。

| 床 | どこから引くか | 描き方 |
|---|---|---|
| **Full-space random** | 2048次元の球面全体から一様 | 大きな楕円の**全体**から出る矢印 |
| **In-plane random（VMIC）** | **上位10主成分が張る平面の内部**から一様 | **小さな円盤の内部に収まる**矢印。**太枠・独自色で強調**（本論文の新規性） |
| **Axis-orthogonal** | 全空間から引いて軸成分を除去 | 軸に**直角記号**を付けた矢印 |

**ICA axes もこの小さな円盤にほぼ収まることが見えるように描く**（実測で上位10主成分空間に
88.7〜99.97% 含まれる）。**これが「なぜ in-plane 床が必要か」の視覚的な説明になる。**

## 描かないもの（重要）

- **必要条件が何個あるか、何が示されたか**（Discussion 依存・PI 判断待ち）
- 結果の数値・有意性・勝敗
- 仮説名（C1〜C4）

## 設計原則（ラボ標準8項目）

階層レイアウト / 色分け3〜5色 / **新規性（in-plane 床）を太枠・独自色で強調** /
破線グルーピング / アイコン活用 / 数式記号併記（`h + alpha*d`, `JS(p, q)`, `d in R^2048`）/
キャプション1文 / テキストは全て枠内に収め端で切らない

## キャプション案（1文）

> Measurement pipeline: activations are taken at the last token of four decoder layers,
> directions are constructed from ICA, from human valence-arousal-dominance ratings and
> from three random controls that differ in the subspace they are drawn from, and the
> effect of injecting each direction is measured as the Jensen-Shannon divergence of the
> next-token distribution.
