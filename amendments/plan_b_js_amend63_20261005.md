# 事前登録 追記63：X2 の評価読み出しは循環している。出力側の読み出しに差し替える

**作成**: 2026-10-05
**対象**: 追記53 BB3 の判定 X2（非対称性）
**判定**: **登録した X2 は循環しており実行しない。出力側の読み出しに差し替える。**
**起動条件**: 本ファイルを commit し push したあとでなければ X2′ を実行しない。
X2 は一度も実行していないため、結果を見てからの変更ではない。

---

## BL1. 登録した X2 に循環がある

追記53 BB3 は次を登録していた。

$$\mathrm{Asym}(a, e) = \frac{\lvert S_{z_a \to e}\rvert}{\lvert S_{w_e \to a}\rvert}$$

> $S_{w_e \to a}$ は $w_e$ への介入による**評価 $a$ の予測値**変化。

**ここが循環している。** 評価 $a$ の予測値は隠れ状態 $h$ に対する線形プローブ
$\hat r_a = v_a^\top h + b_a$ である。介入は $h \leftarrow h + \alpha w_e$ であるから、

$$\hat r_a(h + \alpha w_e) - \hat r_a(h) = \alpha\, v_a^\top w_e$$

**刺激にもモデルの計算にも依存せず、$\alpha$ と内積だけで決まる決定論的な量である。**
これは介入の効果ではなく、**2つの方向の幾何的な関係**を測っているだけである。

同じ理由で $S_{z_a \to e}$ の側も、感情読み出しが隠れ状態プローブであれば循環する。
**本研究の感情読み出しは出力側（13 感情語の次トークン確率）なので、そちらは循環しない。**

**非対称性が出たとしても、それは「$v_a$ と $w_e$ の内積の非対称な正規化」から生じうる。**
したがって登録した X2 は実行しない。

## BL2. 差し替え：評価も出力側で読む

**評価の読み出しを、隠れ状態プローブから出力側の質問応答に替える。**

各評価次元について**二値質問**を用意し、`yes` / `no` の次トークン確率の比を読み出しとする。

$$ R_a(h) = \log \frac{p(\text{yes})}{p(\text{no})} \quad\text{（当該評価次元を問う質問に対して）} $$

介入の効果は追記37 に従い反対称成分で取る。

$$ S_{v \to a} = \tfrac12\big[R_a(h + \alpha v) - R_a(h - \alpha v)\big] $$

**これは出力側の量であり、介入した方向との内積では決まらない。**

### 質問文（21件・本追記で固定する）

| 評価次元 | 質問 |
|---|---|
| suddenness | Did this happen suddenly? |
| familiarity | Had this person been in this kind of situation before? |
| predict_event | Could this event have been predicted? |
| pleasantness | Was this pleasant for the person? |
| unpleasantness | Was this unpleasant for the person? |
| goal_relevance | Did this matter to the person's goals? |
| chance_responsblt | Was this caused by chance? |
| self_responsblt | Was the person responsible for this? |
| other_responsblt | Was someone else responsible for this? |
| predict_conseq | Could the consequences have been predicted? |
| goal_support | Did this help the person's goals? |
| urgency | Did this require immediate action? |
| self_control | Could the person control this? |
| other_control | Could someone else control this? |
| chance_control | Was this outside anyone's control? |
| accept_conseq | Could the person accept the consequences? |
| standards | Did this violate the person's own standards? |
| social_norms | Did this violate social norms? |
| attention | Did the person attend to this closely? |
| not_consider | Did the person try not to think about this? |
| effort | Did this require effort from the person? |

質問文は刺激（crowd-enVENT の記述）に続けて置く。**質問文を結果を見てから変更しない。**

## BL3. 判定 X2′

$$ \mathrm{Asym}(a, e) = \frac{S_{z_a \to e}}{S_{w_e \to a}} $$

ただし**両方とも出力側の読み出し**であり、**両方とも出力摂動量を $J^\*$ に揃える。**

- $S_{z_a \to e}$: 評価方向 $z_a$ への介入による、感情対比 $c_a$ 方向への符号つき効果
  （追記58 の $S$ と同一）
- $S_{w_e \to a}$: 感情方向 $w_e$ への介入による、評価質問の log-odds の符号つき変化

**判定 X2′**: 族として判定する（追記60 の方針に揃える）。
$\overline{S_{Z \to E}}$ と $\overline{S_{E \to Z}}$ をそれぞれ F4 床と比較し、

- **(a)** $\overline{S_{Z \to E}}$ が F4 床の95パーセンタイルを**超える**
- **(b)** $\overline{S_{E \to Z}}$ が F4 床の95パーセンタイルを**超えない**

**(a) かつ (b) が成立すれば非対称性を支持する。**

**前提条件**: (b) 側の読み出しが機能していることを確認する。**評価質問に対する正の対照**
として、当該評価次元を直接問う刺激対（追記56 の Q1〜Q3 の最小対）で log-odds が動くことを
確認する。**動かなければ (b) の不成立を主張しない**（追記49 V3 と同じ非対称な扱い）。

## BL4. この設計でも残る限界（先に書く）

- **二値質問の読み出しは質問文に依存する。** 質問文を変えれば結果が変わりうる。
  **1通りの質問文でしか測っていないことを限界に書く**
- **(b) が超えないことは「効果が無い」ことを意味しない。** 検出できないだけである。
  **「感情方向は評価を動かさない」ではなく「分散を揃えた床のもとで検出できない」と書く**
- 感情方向 $w_e$ は 13 カテゴリの指示変数への回帰であり、$R^2$ が低い。
  **$R^2$ を報告し、低い場合は (b) の解釈に用いない**

## BL5. 約束

- 登録した X2（隠れ状態プローブ）を**実行しない**。循環していた事実を論文に書く
- 質問文 21 件を本追記で固定し、結果を見てから変えない
- (b) の前提条件が落ちた場合、非対称性を主張しない
- 「動かさない」と書かず「検出できない」と書く
