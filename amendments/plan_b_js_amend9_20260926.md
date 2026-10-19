# 事前登録 追記9：CRH（ICML 2026）の対照はノルム整合であって分散整合ではない

**対象**: 追記3 C3（分散較正対照の新規性の扱い）、条件3 の枠づけ
**作成**: 2026-09-26
**状態**: **実験前**
**典拠**: arXiv:2605.01844v2 の PDF 全文（助教が自分で取得し Appendix K.2 を直接読んだ）

---

## I1. 経緯

文献担当の調査で **Cylindrical Representation Hypothesis (CRH, arXiv:2605.01844, ICML 2026 採択)** が条件3 に部分重複する可能性が挙がった。
争点は **Appendix K.2「Probing on a Random Cylinder」** の対照設計であった。ar5iv・arXiv の HTML はいずれも Appendix E 以降が切れており到達できなかったため、**助教が PDF を取得して直接読んだ**（1回目のダウンロードは xref が壊れており再取得した）。

## I2. K.2 の対照の実際（原文）

> "**Setup.** We run a matched null control on Gemma-2B-IT at layer 9. We use the same probing objective and **the same norm budget** as the main probe. The only change is that we replace the PCA-derived cylinder directions with **random directions**."

> "**Result.** The optimized directions produce stronger axis and phase structure, while the random directions produce a much flatter landscape. … Therefore, **only semantically meaningful direction and normal plane can produce structured loss landscapes**."

数値（Table 4、Gemma-2B-IT 層9）: 平均損失 38.72 対 39.80、損失の標準偏差 3.43 対 1.16、軸方向の範囲 6.05 対 1.59、位相方向の範囲 0.51 対 0.07。

## I3. 判定：条件3 は先取りされていない

**CRH の対照は「ノルム予算を揃えた無作為方向」である。** 論文は**無作為方向が最適化方向と同じ部分空間あるいは同じ分散プロファイルから引かれているとは述べていない。**

**そして結論は「意味的に有意味な方向と法線平面だけが構造化された損失地形を生む」である。これは、我々の条件3 が「分散を揃えた対照なしには導けない」と言っている型の推論そのものである。**

**したがって CRH は条件3 を先取りしていない。むしろ条件3 が指摘する実践の実例である。** 追記3 C3 の「既に使われている対照が必要であることを実証した」という枠づけは維持でき、**実例が1件増えた。**

## I4. ただし書き方に3つの制約を課す（過剰主張の防止）

1. **「全空間から引いている」と断定しない。** 原文は "random directions" とのみ書いており、どの空間から引いたかを明示していない。**書けるのは「無作為方向がノルム予算のみで整合されており、部分空間や分散プロファイルとの整合は述べられていない」までである**
2. **成果指標が違うことを明記する。** CRH は**損失地形の構造**を見ており、我々は**出力分布の変化**を見ている。設定が同一ではないので、**CRH の個別の結論が誤りであるとは主張しない**
3. **ICML 2026 の採択論文である。** 批判的に扱わず、**「同じ問題が最新の査読済み研究にも現れる」という形で、条件3 の必要性の傍証として引用する**

## I5. 併せて確定したこと（追記3 の更新）

- **機構は独立**である。CRH は分離可能性・分散に基づく指標が結果を予測しないと明示的に述べている（"separability estimates…do not always correlate well with actual steering outcomes"）。**我々の分散比例性の主張は CRH と両立せず、独立の貢献である**
- **定性的現象（表象部分空間内のどこに方向があるかが結果に影響する）は CRH が先行**する。**ここは引用し、「我々が示した」と書かない**
- **in-plane 対照の先例は Sun et al. (arXiv:2604.03147) のみ**である。CRH は in-plane 対照を用いていない

## I6. 記録

**この確認は実験前に完了した。** 追記3 C3 で「必要性の実証として維持する」と保守的に書いた判断は、全文確認によって裏付けられた。
**HTML 版が途中で切れていたため、PDF を取得するまで判定を保留した。** 集約された HTML や二次情報で判定しなかったことを記録する。
