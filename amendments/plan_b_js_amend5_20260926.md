# 事前登録 追記5：G4 のベンチマークを GSM8K と MATH に確定する（AIME は使わない）

**対象**: `plan_b_js_prereg_20260926.md` §2 G4、追記2 B3、追記4 D2
**作成**: 2026-09-26
**状態**: **実験前。** push 前
**典拠**: `01_調査/ベンチマークのライセンス確認_20260926.md`（文献担当・一次確認）

---

## E1. 使うベンチマークを2件に確定する

**元の事前登録は「主要ベンチマーク1件」としか書いていなかった。走る前にここで確定させる。**

| データセット | ライセンス | 根拠 | 決定 |
|---|---|---|---|
| **GSM8K**（`openai/gsm8k`） | MIT（Copyright (c) 2021 OpenAI） | GitHub `openai/grade-school-math` の LICENSE 実物＋HF カードの二重確認 | **主ベンチマークとして使用** |
| **MATH**（`hendrycks/competition_math`） | MIT（Copyright (c) Dan Hendrycks, 2021） | GitHub `hendrycks/math` の LICENSE 実物＋HF メタデータの二重確認 | **副ベンチマークとして使用** |
| **AIME** | **不明（グレー）** | 問題の著作権は Mathematical Association of America に帰属。HF 上の各データセットが表示する Apache 2.0 等は**データセット作成者が付したもので、MAA 著作物の再利用を許諾する権限を持つ主体の表示ではない** | **使わない** |

## E2. AIME を使わない判断（助教）

**理由は2つ。**

1. **法的リスクに対して科学的な見返りがない。** G4 が必要とするのは「トークン予算を増やすと精度が上がる曲線」であり、**GSM8K（小学校算数・1,319問）と MATH（競技数学・12,500問・難易度5段階）で難易度の幅は十分に取れる。** AIME を加えても曲線の形についての結論は変わらない
2. **我々はコード公開を前提にしている。** 再配布可否が不明な素材を含めると、公開時点で問題が顕在化する。**投稿後に気づくより、使わない方が安い**

**MAA への事前問い合わせは行わない。** 待ち時間に見合う利得がない。**将来 AIME が必要になった場合は、その時点で問い合わせる。**

## E3. 主張の書き方に付ける制約

- **「難問で有効」と書く場合、根拠は MATH の難易度上位層に限る。** AIME を使っていないので、競技レベル最上位への外挿は書かない
- **限界として明記する**: 「評価は GSM8K と MATH に限る。AIME 等のより難しいベンチマークは、問題の著作権の所在が不明であるため使用しなかった」
- **主ベンチマーク = GSM8K。** 追記4 D2 の判定基準（軸Xの前線が人間VAD 3本すべてをトークン範囲の3分の1以上の区間で上回る）は **GSM8K で判定する**。MATH は**感度分析**とする。**主判定を後から MATH に移さない**

## E4. データの扱い

- **GSM8K**: MIT なので同梱可。**著作権表示と MIT 本文を同梱する**
- **MATH**: MIT だが12,500件で大きいため、**リンクと取得スクリプトのみを公開する**（同梱しない）
- 取得は HuggingFace datasets 経由。**API キーは使わない**

## E5. 引用（文献担当が著者全員を確認済み）

- GSM8K: Karl Cobbe, Vineet Kosaraju, Mohammad Bavarian, Mark Chen, Heewoo Jun, Lukasz Kaiser, Matthias Plappert, Jerry Tworek, Jacob Hilton, Reiichiro Nakano, Christopher Hesse, John Schulman (2021), arXiv:2110.14168
- MATH: Dan Hendrycks, Collin Burns, Saurav Kadavath, Akul Arora, Steven Basart, Eric Tang, Dawn Song, Jacob Steinhardt (2021), arXiv:2103.03874

**`et al.` を使わず全員を書く。**

## E6. G4 実行前の前提条件（再掲・変更なし）

**選んだモデルで介入なしのベースライン曲線が平らでないことを先に確認する。** GSM8K 500問、トークン予算4点（64 / 128 / 256 / 512）で精度が単調に上がり、**最小予算と最大予算の差が5ポイント以上**あること。
**満たさなければそのモデルで G4 は測定不能**とし、停止して報告する。モデル変更は助教が決める。
