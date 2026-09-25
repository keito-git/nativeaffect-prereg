# 引き継ぎ: 論文2 Methods・Results の執筆（中村 → 渡辺さん）

2026-09-26 / 野村先生指示。**Discussion と Intro は PI の枠組み判断（A/B/C）待ちのため着手しない。**
執筆順はラボ方針の Methods → Results → Discussion → Intro → RW に従う。
骨格: `04_原稿/日本語版/00_骨格アウトライン_20260926.md`（本書と併せて読むこと）

---

## 0. 最初に読むもの（順序厳守）

1. `/path/to/research/論文構成ルール_the group標準.md`（構成が優先）
2. `/path/to/research/the supervisor論文/執筆スタイルガイド.md`（文体・図表慣例）
3. `03_解析/preregistration/axis_rebuilt_prereg_20260925.md` の **§37・§48・§50・§51・§52**
   （確証仮説、3ゲート、検証群結果、位置づけ、**再現行数の訂正**）

---

## 1. 数値の典拠（**手打ち禁止・投稿前に機械照合**）

| 内容 | ファイル |
|---|---|
| C1〜C4 の判定と全セル値 | `03_解析/confirmation/adjudication_confirmation.json` |
| 発見群の同形式 | `03_解析/_gate1_smoke/adj_discovery_validation.json` |
| 検証群の生結果（C1・C2） | `03_解析/confirmation/pos_ctrl_inplane_confirmation_20260925T210056Z.json` |
| 検証群の生結果（C4） | `03_解析/confirmation/inplane_floor_confirmation_20260925T210454Z.json` |
| 整合（C3・主/副） | `03_解析/axes_nopad/alignment_primary.json`・`s3_categories.json` |
| 手続き依存 | `03_解析/axes_nopad/procedure_dependence.json` |
| シード安定性 | `03_解析/axes_nopad/seed_stability_c3.json`・`03_解析/pos_ctrl_inplane_seeds/` |
| 符号付き読み出し | `03_解析/signed_valence/signed_valence_20260925T200619Z.json` |

表の生成は `python/phase10/conf_table.py --adj <判定JSON>` を使うと markdown が出る。
**本文・表の数値は必ずこの出力か JSON から取る。**

## 2. 必ず守る記述（野村確定・§51/§52）

1. **「11/12敗」を見出しにしない。** §52.4 の確定文をそのまま使う
2. **C1 の本文数値は検証群（1.795〜2.429、約1.8〜2.4倍）。** 発見群（1.936〜2.731、約2〜3倍）は併記。
   **層10・12 の余裕が 0.30 程度しかない**ことを書く
3. **「効果量を伴う再現は3行」と書く**（層5軸2・層7軸1・層12軸0）。**「5行が再現した」とは書かない。**
   5 という数を出す場合は**必ず同じ文の中に内訳を入れる**（残る2行＝層5軸1・層10軸2 は
   Cliff's δ=+0.00 のセルでのみ有意であり実質的な再現ではない）。§53.1 で確定
4. **セル同一性の比較は事前登録していない。**「事前登録した確証仮説ではないが、独立な分割を
   またいで再現した観察」と明示する。**事前登録した仮説と未登録の観察を必ず区別する**
5. **C3 は「発見群と同一値であり out-of-sample の情報を持たない」と明記**し、
   C1・C2・C4 が真に out-of-sample であることと対比する
6. **C2b 層10 で mean_diff の符号が正に転じた**ことをそのまま書く（有意からは遠い）
7. 符号付き読み出しは規準未達。**「部分的に支持」とは書かない**
8. **BH 族を常に明示する**（C4 は 48、C1/C2a は 20、C2b は 16）。§52.5 の教訓

## 3. Fig.3（完成済み・本論文の中核）

`04_原稿/図表/fig3_split_replication.pdf`（生成コード `python/phase10/fig3_split_replication.py`）

- 層×軸（12行）× α（0.03/0.05/0.1/0.2）の Cliff's δ ヒートマップを**発見群/検証群で並置**
- 有意性は**太枠＋中心マーカーの二重符号化**（色だけに依存しない・色覚バリアフリー）
- 左の ◆ は**両群で有意な行**（5行）
- canvas 5.44×3.98 in、`\linewidth`（371.6pt）で縮小率 0.949、刷り上がり最小フォント 7.02 pt
- **キャプションは原則1文。** 本文で必ず言及する（図表の放置禁止）

## 4. 執筆する範囲（今回）

- **Methodology（6小節 A〜F）**: 骨格アウトライン §4 のとおり。問題定義を最初に
- **Experiments（7小節 A〜G）**: 骨格アウトライン §5 のとおり。設計→結果の順。
  **各小節に固有の図表**（PI 方針）
- Discussion・Intro・RW・Abstract・タイトル確定は**着手しない**

## 5. タイトル候補（野村先生の指摘を受けた再提出・「Emotion Axes」不可）

**理由**: 論文の限定の核心が「**感情固有性は未証明**」なので、軸を "Emotion Axes" と
断定するとタイトルが本文の限定と矛盾する。軸の性質を断定しない語にする。
規定（11〜17語・コロン副題なし・複合形容詞1つ以上）は3案とも充足。

1. **Variance-Matched In-Plane Controls for Credible Steering Claims in Affective Representation Analysis of Large Language Models**（15語）
   → 領域として感情を扱ったことのみ示し、軸の性質を断定しない
2. **Variance-Matched Random Controls for Auditing Intervention Claims on Candidate Emotion Directions in Large Language Models**（15語）
   → "Candidate" で未証明であることを明示
3. **Reproducibility-Aware Auditing of Emotion-Related Directions in Large Language Models Based on Variance-Matched In-Plane Controls**（14語）
   → "Emotion-Related" と "Reproducibility-Aware"（分割再現が中核であることを示す）

→ **渡辺さんと野村先生で確定**。私の推奨は候補3（分割再現という本論文最大の所見が
タイトルに入るため）。略称は **VMIC**（Variance-Matched In-plane Control）を想定。

## 6. ビルドと引用の実務（論文1の実害からの申し送り・必読）

1. **`build.sh` 相当のビルド検査を論文2にも用意する。** 論文1では pdflatex が
   **「エラー0」で全50引用を `[?]` にした PDF** を出し、さらに**終了コード1を返しながら
   12頁の PDF を作った**。**終了コードでは判断できない。** ログの `! ` 行・PDF 内の `[?]`・
   プレースホルダ・日本語混入を**機械検査し、満たさなければ PDF を出さない**形にする。
   流用元: `/path/to/research/論文/AffectGeometry_LLM内部感情表現の幾何/04_原稿/投稿関連/build.sh`
2. **bib の来歴メモは `%` コメントにのみ書く。** `note` フィールドに日本語を入れると
   組版で落ちる（論文1で実害）
3. **主張を1つ立てたら、その時点でその主張の文言そのものを検索する。** 論文1では書き終えた
   後に先取り論文が4件見つかった。**テーマではなく現象の記述で検索する**
   （例: 「in-plane random control」「variance-matched random direction」
   「steering direction beats random baseline」など）
4. 引用は**2023年以降を優先・25〜35件**。**捏造は絶対禁止**。著者名はフルネーム・全員列挙
   （`et al.` 不可）。存在を確認していない文献は引用しない

## 7. 私（中村）への確認が必要な場合

数値の解釈・追加解析・図の修正が必要なら中村に依頼してください。
**結果ファイルにない数値を推測で書かないこと。** 不明な点は必ず問い合わせてください。
