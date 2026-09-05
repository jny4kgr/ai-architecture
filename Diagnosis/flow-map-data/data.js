// 業務フローmap データ：株式会社ランドスタイル「新築分譲 Lancasa」1棟の一生
// 出典:
//  1) Diagnosis/01_ランドスタイル業務フロー仮説.md（同社固有の仮説。★=未確認）
//  2) Research/ランドスタイル調査と差別化戦略.md（会社調査）
//  3) research/workflows/new-build-housing-developer.md（業界一般16ステップ・時間推定）
// unknown配列を持つノードは assumed:true（レポートに無い/★未確認のため業界一般から想定）。
window.FLOW_DATA = {
  meta: {
    company: "株式会社ランドスタイル",
    line: "新築分譲 Lancasa 1棟の一生",
    hourly: 2000,
    start: "仲介業者から売地情報を受け取る（仕入の引き金）",
    end: "残代金入金（決済・引渡完了）",
    notes: "土地代・建築費は別途。土地仕入代金そのものと自社施工の元請本体工事費はmoney_out/external_costに計上しない。external_costは社外（測量・地盤調査・確認検査機関・保険法人・協力業者・パース外注・司法書士・客付け仲介会社）へ支払う費用のみを計上。仲介手数料支払(n56)は他社仲介経由で成約した場合のみ発生する分岐で、自社客付けの場合は発生しない。金額はいずれも業界相場からの粗い推定で、実額は社長ヒアリングでの確認が前提。"
  },
  lanes: [
    { id: "shacho", name: "社長" },
    { id: "eigyo", name: "営業" },
    { id: "sekkei", name: "設計" },
    { id: "koumu", name: "工務（現場監督）" },
    { id: "jimu", name: "事務経理" },
    { id: "ext_kokyaku", name: "買主・仲介会社・銀行", external: true },
    { id: "ext_gyousha", name: "協力業者・外注(測量/地盤/パース/職人)", external: true }
  ],
  blocks: [
    { id: "b1", name: "土地情報入手・用地判断" },
    { id: "b2", name: "買付・仕入契約・決済" },
    { id: "b3", name: "設計・確認申請" },
    { id: "b4", name: "発注・下請契約" },
    { id: "b5", name: "造成・着工・施工管理" },
    { id: "b6", name: "検査" },
    { id: "b7", name: "販売準備・集客" },
    { id: "b8", name: "業者間配信・ポータル掲載・反響対応" },
    { id: "b9", name: "売買契約・ローン" },
    { id: "b10", name: "決済・引渡・入金・アフター" }
  ],
  nodes: [
    // ===== b1 土地情報入手・用地判断 =====
    { id: "n1", block: "b1", lane: "eigyo", name: "仲介業者から売地情報を電話で受ける", trigger: "仲介業者からの電話", tool: "電話", input: "口頭（所在地・面積・価格）", output: "口頭メモ", minutes: 10, freq: 1, assumed: true, unknown: ["主な入手経路の比率(電話/FAX/メール/LINE)"], note: "業界一般では業者からの情報はFAX・メール添付・LINEに分散(新築分譲業界フロー ステップ1)。ランドスタイルの実際の比率は仮説シート★未確認" },
    { id: "n2", block: "b1", lane: "eigyo", name: "売地情報のFAX/PDFを受信する", trigger: "業者からのFAX送信/メール添付", tool: "FAX複合機／Gmail", input: "物件概要書（紙／PDF）", output: "紙／PDF", minutes: 5, freq: 1, assumed: true, note: "業界一般ステップ1の想定" },
    { id: "n3", block: "b1", lane: "eigyo", name: "物件概要を仕入れ検討リストに手入力する", trigger: "情報受信後", tool: "Excel（仕入れ検討リスト）", input: "物件概要書", output: "仕入れ検討リストExcel", minutes: 15, freq: 1, assumed: true, unknown: ["検討リストがExcelか紙か・管理表の有無"], note: "仮説シート★「収支Excelが物件ごとの別ファイルなら統一の余地」に関連。検討リストの形式自体も未確認" },
    { id: "n4", block: "b1", lane: "sekkei", name: "現地確認・法規調査を行う", trigger: "検討リストで一次通過", tool: "現地（カメラ・メジャー）＋市役所窓口（建築指導課等）", input: "用途地域・建ぺい容積等の公開情報", output: "現地写真・法規調査メモ", minutes: 180, freq: 1, assumed: true, unknown: ["調査項目チェックリストの有無", "誰が同行するか(兼務実態)"], note: "業界一般ステップ2。ランドスタイルは一級建築士が女性1名体制のため兼務が疑われる(仮説シート★)" },
    { id: "n5", block: "b1", lane: "shacho", name: "事業収支をExcelでシミュレーションする", trigger: "法規調査完了", tool: "Excel（収支表）", input: "想定売価・建築費・諸経費・金利", output: "収支シミュレーションExcel", minutes: 90, freq: 1, assumed: true, unknown: ["収支Excelが物件ごとに何種類あるか", "仕入れ判断基準(利益率・回転期間)の明文化有無"], note: "仮説シート★「収支Excelが物件ごとの別ファイルなら統一の余地」" },
    { id: "n6", block: "b1", lane: "shacho", name: "仕入れ可否を判断する", trigger: "収支シミュレーション完了", tool: "口頭（社内検討）", input: "収支シミュレーション", output: "仕入れ判断（GO/NO）", minutes: 30, freq: 1, assumed: true, note: "業界一般ステップ2〜3の想定" },

    // ===== b2 買付・仕入契約・決済 =====
    { id: "n7", block: "b2", lane: "shacho", name: "買付証明書を作成し売主・仲介へ提出する", trigger: "仕入れGO判断", tool: "Word（自社ひな形）＋FAX／メール", input: "収支シミュレーション・希望条件", output: "買付証明書（提出済み）", minutes: 40, freq: 1, wait: "売主の回答待ち 平均数日", assumed: true, note: "業界一般ステップ3。買付証明はスピード勝負とされる(出典: zennichi.or.jp)" },
    { id: "n8", block: "b2", lane: "jimu", name: "土地売買契約書を準備する", trigger: "買付証明書が通る", tool: "Word（自社ひな形）", input: "買付証明書・重説資料", output: "土地売買契約書", minutes: 60, freq: 1, assumed: true },
    { id: "n9", block: "b2", lane: "shacho", name: "土地売買契約を締結する（重説含む）", trigger: "契約書準備完了", tool: "対面・押印", input: "契約書・重説", output: "締結済み契約書", minutes: 90, freq: 1, assumed: true },
    { id: "n10", block: "b2", lane: "jimu", name: "決済日程を金融機関・司法書士と調整する", trigger: "契約締結後", tool: "電話", input: "決済希望日", output: "決済日確定", minutes: 40, freq: 1, wait: "関係者調整に数日", assumed: true },
    { id: "n11", block: "b2", lane: "ext_kokyaku", name: "決済・所有権移転を行う（土地代金支払）", trigger: "決済日到来", tool: "銀行窓口・司法書士立会", input: "締結済み契約書", output: "登記・鍵", minutes: 0, freq: 1, assumed: true, note: "土地仕入代金そのものはmoney_outとして計上せず、meta.notesに別記" },

    // ===== b3 設計・確認申請 =====
    { id: "n12", block: "b3", lane: "sekkei", name: "商品企画・プランを検討する", trigger: "決済後（土地確定）", tool: "〇〇CAD／手描き", input: "敷地条件・Lancasaブランドコンセプト（女性目線の家事動線）", output: "プラン図（ラフ）", minutes: 300, freq: 1, assumed: true, unknown: ["設計担当の人数・兼務実態"], note: "事実: 女性一級建築士1名が看板(調査報告書1章)。仮説シート★「申請図書のボトルネックが1人に集中している疑い」" },
    { id: "n13", block: "b3", lane: "sekkei", name: "実行予算（原価目標）をExcelで作成する", trigger: "プラン確定", tool: "Excel（実行予算書）", input: "プラン図・標準仕様", output: "実行予算Excel", minutes: 180, freq: 1, assumed: true, unknown: ["単価マスタの有無・最終更新日", "実行予算が物件ごとに別ファイルか"], note: "業界一般ステップ4「実行予算Excelが物件ごとにコピーされ標準仕様の更新が反映されない」を想定" },
    { id: "n14", block: "b3", lane: "sekkei", name: "意匠図・構造関係図書・省エネ関連図書を作成し確認申請を提出する", trigger: "実行予算確定", tool: "〇〇CAD＋確認検査機関の窓口／申請システム", input: "プラン図・法規調査メモ", output: "申請図書一式・確認申請受付", minutes: 1200, freq: 1, wait: "確認済証まで概ね1.5週間(事前審査・補正往復含む)", redo: "補正指摘への対応が1〜2回発生(業界一般の目安)", assumed: true, unknown: ["2025年4月法改正後の作成時間の増分", "申請ステータス管理表の有無"], note: "業界一般ステップ5。2025年4月の4号特例縮小・省エネ適合義務化で図書作成負荷が増加(出典: andpad.jp)。仮説シート★「設計者が実質1名なら会社最大のボトルネック」" },
    { id: "n15", block: "b3", lane: "ext_gyousha", name: "測量を外注する", trigger: "申請図書作成に必要な確定測量", tool: "メール発注", input: "敷地条件", output: "測量図", minutes: 15, freq: 1, wait: "納品まで数日", assumed: true, external_cost: { amount: 150000, to: "測量事務所", item: "確定測量" }, note: "金額は業界相場からの粗い推定" },
    { id: "n16", block: "b3", lane: "ext_gyousha", name: "地盤調査を外注する", trigger: "着工前の地盤確認", tool: "メール発注", input: "敷地情報", output: "地盤調査報告書（SWS試験等）", minutes: 15, freq: 1, wait: "調査・報告まで数日", assumed: true, external_cost: { amount: 80000, to: "地盤調査会社", item: "地盤調査(SWS試験等)" }, note: "金額は業界相場からの粗い推定" },
    { id: "n17", block: "b3", lane: "jimu", name: "確認申請手数料を支払い瑕疵保険を申込む", trigger: "確認済証取得の見込み", tool: "保険法人インターネット申込", input: "申請図書・確認申請番号", output: "確認申請手数料支払・瑕疵保険申込", minutes: 40, freq: 1, wait: "保険証券発行まで1〜10日", assumed: true, unknown: ["利用している保険法人", "住宅性能表示・長期優良住宅の取得有無"], external_cost: { amount: 150000, to: "指定確認検査機関", item: "確認申請手数料" }, note: "仮説シート★「瑕疵保険はどこの保険法人か」" },
    { id: "n62", block: "b3", lane: "jimu", name: "瑕疵保険料を振り込む", trigger: "瑕疵保険証券発行決定", tool: "銀行振込", input: "保険料請求", output: "振込完了", minutes: 10, freq: 1, assumed: true, external_cost: { amount: 120000, to: "住宅瑕疵担保責任保険法人", item: "瑕疵担保責任保険料" }, note: "金額は業界相場(まもりすまい保険等)からの粗い推定" },

    // ===== b4 発注・下請契約 =====
    { id: "n19", block: "b4", lane: "koumu", name: "協力業者へ見積依頼書を作成し図面と一緒にメール送付する", trigger: "確認申請提出後", tool: "Word／Excelひな形＋メール", input: "図面PDF・工種・数量・見積提出期限", output: "見積依頼書メール", minutes: 40, freq: 5, assumed: true, unknown: ["1棟あたりの見積依頼社数", "固定業者と相見積の比率"], note: "仮説シート★「固定業者と相見積の比率次第。固定が多いなら効果は小さい」。建設業法上の法定見積期間・14項目提示義務がある(業界一般ステップ6)" },
    { id: "n20", block: "b4", lane: "koumu", name: "返送された見積をExcelの比較表に転記する", trigger: "業者から見積返信", tool: "Excel", input: "業者からの見積書（PDF/紙）", output: "見積比較表Excel", minutes: 60, freq: 1, redo: "科目・単位の粒度が業者ごとに違うため転記のやり直しが発生(業界一般の指摘)", assumed: true },
    { id: "n21", block: "b4", lane: "shacho", name: "発注業者を決定する", trigger: "見積比較表完成", tool: "口頭（社内検討）", input: "見積比較表", output: "発注先決定", minutes: 30, freq: 1, assumed: true },
    { id: "n22", block: "b4", lane: "jimu", name: "発注書・下請契約書面を作成し送付する", trigger: "発注先決定", tool: "Excel／Wordひな形＋印刷・押印", input: "発注台帳（物件情報）", output: "発注書（紙／PDF）", minutes: 90, freq: 5, assumed: true, unknown: ["発注書が紙・FAX・PDFメールのどれか", "1棟あたりの発行枚数"], note: "仮説シート★「紙かFAXかPDFか、1棟何枚か」。建設業法上7年間の保管義務(出典: any-one.jp)" },
    { id: "n23", block: "b4", lane: "ext_gyousha", name: "協力業者から注文請書を受領する", trigger: "発注書送付後", tool: "郵送／FAX", input: "発注書", output: "注文請書", minutes: 10, freq: 5, wait: "返送まで数日〜数週間(未返送は催促が必要になることがある)", assumed: true },

    // ===== b5 造成・着工・施工管理 =====
    { id: "n24", block: "b5", lane: "koumu", name: "工程表をExcelで作成し職人に配る", trigger: "発注完了", tool: "Excel（ガント形式）＋印刷・FAX", input: "着工日・完了予定日・各工種の作業日数", output: "紙／FAXの工程表", minutes: 120, freq: 1, assumed: true, unknown: ["工程連絡がLINE個別かグループか"], note: "仮説シート★「LINE個別かグループか」。業界一般では紙の工程表配布は更新のタイムラグが致命的とされる(出典: buildynote.com)" },
    { id: "n25", block: "b5", lane: "ext_gyousha", name: "造成・基礎工事を施工する", trigger: "工程表の着工日", tool: "—", input: "図面・地盤調査報告書", output: "現場（基礎完了）", minutes: 0, freq: 1, assumed: true, external_cost: { amount: 12000000, to: "協力業者数社(土工・基礎)", item: "造成・基礎工事外注" }, note: "金額は浜崎2号棟クラス(延床約120㎡・3階建てガレージハウス)の規模感からの粗い推定" },
    { id: "n26", block: "b5", lane: "koumu", name: "現場を巡回し進捗を確認する", trigger: "毎日〜週次", tool: "現場訪問", input: "現場", output: "巡回結果(記憶／口頭)", minutes: 60, freq: 15, assumed: true, unknown: ["1人の現場監督が何棟掛け持ちしているか"], note: "業界一般では現場監督1人が複数現場を掛け持ちするのが通例(業界一般ステップ8)。ランドスタイルは工事部2名の内訳・掛け持ち状況は仮説シート★" },
    { id: "n27", block: "b5", lane: "koumu", name: "現場写真を撮りLINEで報告する", trigger: "巡回時・工程完了時", tool: "スマホ＋LINE", input: "現場", output: "LINE写真", minutes: 15, freq: 15, assumed: true, unknown: ["写真の保管場所(LINEのままかフォルダ整理か)"], note: "仮説シート★「LINE個別かグループか。写真の保管場所がバラけている可能性」" },
    { id: "n28", block: "b5", lane: "koumu", name: "工程が1日ズレた際に関係業者へ電話で再連絡する", trigger: "天候・遅延発生", tool: "電話", input: "工程表の変更", output: "口頭連絡", minutes: 45, freq: 3, redo: "遅延のたびに再発生", assumed: true, unknown: ["何人に連絡し直すか"], note: "仮説シート★「工程が1日ズレたときの再連絡が地味に重い」" },
    { id: "n29", block: "b5", lane: "ext_gyousha", name: "上棟・建方工事を施工する", trigger: "工程表の上棟日", tool: "—", input: "図面", output: "現場（上棟完了）", minutes: 0, freq: 1, assumed: true, external_cost: { amount: 15000000, to: "協力業者数社(大工・建方)", item: "建方・木工事外注" }, note: "金額は規模感からの粗い推定" },
    { id: "n30", block: "b5", lane: "ext_gyousha", name: "内外装・設備工事を施工する", trigger: "上棟後の工程", tool: "—", input: "図面・仕様書(外壁：ニチハ モエンサイディング等)", output: "現場（竣工）", minutes: 0, freq: 1, assumed: true, external_cost: { amount: 18000000, to: "協力業者数社(内外装・設備)", item: "内外装・設備工事外注" }, note: "事実: 受領図面は外壁製品名・色番(ニチハ モエンサイディングM14 グレー×ホワイト×ヴィンテージウッドブラウン等)まで明記(調査報告書2章)。金額は規模感からの粗い推定" },
    { id: "n31", block: "b5", lane: "jimu", name: "出来高を確認し請求書と発注書を照合する【月次締め】", trigger: "月末", tool: "紙の請求書＋Excel（支払一覧）", input: "協力業者請求書・発注書", output: "支払一覧Excel・振込データ", minutes: 240, freq: 3, redo: "工種・工事番号の記載粒度が業者ごとに違うため確認に時間がかかる(業界一般の指摘)", assumed: true, unknown: ["月に何社・何枚の請求書を処理するか", "会計ソフトの種類・CSV取込対応"], note: "仮説シート・業界一般ステップ11(週3.0h＝業界1位の負荷)を統合。ランドスタイルの実数は★未確認" },

    // ===== b6 検査 =====
    { id: "n32", block: "b6", lane: "koumu", name: "瑕疵保険の現場検査(基礎配筋・屋根時)を受ける", trigger: "基礎配筋完了／屋根工事完了", tool: "保険法人検査員の立会", input: "現場", output: "検査合格", minutes: 60, freq: 2, wait: "検査申込から日程確定まで数日", assumed: true },
    { id: "n33", block: "b6", lane: "koumu", name: "中間検査(該当する場合)・完了検査を申請し立会する", trigger: "指定工程完了後4日以内／工事完了後4日以内", tool: "検査機関の申込システム", input: "工程写真・竣工図", output: "検査済証", minutes: 120, freq: 1, assumed: true, unknown: ["埼玉県内対象自治体で木造2階建ての中間検査指定工程があるか"], note: "仮説シート・業界一般ステップ10。中間検査の要否は自治体差があるため★(出典: city.yokohama.lg.jp)" },
    { id: "n34", block: "b6", lane: "jimu", name: "瑕疵保険証券の発行を申請する", trigger: "現場検査合格", tool: "保険法人インターネット申込", input: "検査合格通知", output: "保険証券", minutes: 30, freq: 1, wait: "発行まで1〜10日", assumed: true },

    // ===== b7 販売準備・集客 =====
    { id: "n35", block: "b7", lane: "shacho", name: "販売価格を決定する", trigger: "竣工めど(工程確定)", tool: "口頭(社内検討)", input: "実行予算・周辺相場(SUUMO/レインズ成約事例)", output: "販売価格決定", minutes: 60, freq: 1, assumed: true, note: "事実: Lancasaは4,000〜6,880万円の準高価格帯(調査報告書1章)。浜崎2号棟は6,880万円でエリア内最高値挑戦物件(調査報告書4章)" },
    { id: "n36", block: "b7", lane: "eigyo", name: "物件概要をマイソクにまとめる", trigger: "価格決定後", tool: "Excel／PowerPoint(マイソクひな形)", input: "プラン図・物件概要・価格", output: "マイソクPDF", minutes: 90, freq: 1, assumed: true, unknown: ["マイソクひな形の形式・営業が商談で実際に使う資料の実物"], note: "報告書ヒアリング項目「営業さんが商談で実際に使う資料を見せてもらえますか」に対応" },
    { id: "n37", block: "b7", lane: "ext_gyousha", name: "外観パース・内観パース・動画を外注する", trigger: "竣工前の販売開始準備", tool: "メール発注", input: "立面図・仕上げ表(製品名・色番明記)", output: "外観パース(昼・夕)・内観パース・15秒動画", minutes: 20, freq: 1, wait: "納品まで数日", assumed: true, unknown: ["現在の外注先・1枚あたり単価・納期(パースは今どうしているか)"], external_cost: { amount: 60000, to: "パース制作事務所", item: "外観パース・内観パース・動画一式" }, note: "事実: 受領図面は外壁製品名・色番まで明記され公正競争規約対応可能な精度(調査報告書2章)。外注の実態は報告書ヒアリング項目「パースは今どうしていますか」で★未確認" },
    { id: "n38", block: "b7", lane: "eigyo", name: "現地で写真を撮影する", trigger: "竣工または内覧会準備", tool: "デジカメ／スマホ", input: "現地", output: "現地写真", minutes: 60, freq: 1, assumed: true, note: "事実: SUUMO掲載写真に浴室・玄関・収納・トイレが無い(建築前で実写が撮れない状態、調査報告書3章)" },
    { id: "n39", block: "b7", lane: "eigyo", name: "紹介文・キャッチコピーを作成する", trigger: "写真・マイソク素材そろう", tool: "Word", input: "物件特徴・Lancasaキャッチ「建てたいが叶う家づくり」", output: "紹介文テキスト", minutes: 45, freq: 1, assumed: true },

    // ===== b8 業者間配信・ポータル掲載・反響対応 =====
    { id: "n40", block: "b8", lane: "eigyo", name: "客付け仲介業者へ物件情報をFAXで一斉配信する", trigger: "販売開始", tool: "FAX一斉送信", input: "マイソクPDF", output: "FAX送信(記録なし)", minutes: 40, freq: 1, assumed: true, unknown: ["物件情報を流している業者数・管理方法(Excel/FAX送信リスト/メールグループ)"], note: "事実: 自社サイトに「販売業者様専用ページ」があり業者間配信の実態を示す(調査報告書4章)。仮説シート★「業者間配信が売上の命綱」。配信手段の内訳は報告書ヒアリング項目で★未確認" },
    { id: "n41", block: "b8", lane: "eigyo", name: "客付け仲介業者へメールで一斉配信する", trigger: "販売開始", tool: "メール一斉送信", input: "マイソクPDF", output: "送信メール", minutes: 30, freq: 1, assumed: true },
    { id: "n42", block: "b8", lane: "eigyo", name: "SUUMO管理画面に物件情報・写真を入力する", trigger: "販売開始", tool: "SUUMO管理画面", input: "物件概要・写真・紹介文", output: "SUUMO掲載", minutes: 60, freq: 1, assumed: true, unknown: ["掲載作業の担当者・所要時間"], note: "事実: SUUMO掲載13件。浜崎物件は浴室・玄関・収納・トイレの写真が無く写真充実度スコアで減点状態、同エリア競合(飯田グラファーレ)は実写33〜53枚(調査報告書3章)。作業時間は報告書ヒアリング項目「SUUMOの掲載作業は誰がやっていますか」で★未確認" },
    { id: "n43", block: "b8", lane: "eigyo", name: "アットホーム管理画面に物件情報・写真を入力する", trigger: "販売開始", tool: "アットホーム管理画面", input: "物件概要・写真・紹介文", output: "アットホーム掲載", minutes: 45, freq: 1, assumed: true, note: "事実: アットホーム掲載10件(調査報告書3章)" },
    { id: "n44", block: "b8", lane: "eigyo", name: "レインズ／ATBBに登録する", trigger: "販売開始", tool: "レインズ／ATBB入力画面", input: "物件概要", output: "レインズ／ATBB掲載", minutes: 30, freq: 1, assumed: true, note: "売主物件のレインズ登録は法的義務ではなく運用は会社判断(業界一般ステップ13、出典: reins.or.jp)。ランドスタイルの実施有無は未確認" },
    { id: "n45", block: "b8", lane: "eigyo", name: "ポータル反響メールを確認し反響管理表に転記する", trigger: "反響メール受信", tool: "メール＋Excel(反響管理表)", input: "反響メール(氏名・希望条件)", output: "反響管理表Excel", minutes: 15, freq: 6, assumed: true, unknown: ["反響の主な流入経路の比率(SUUMO/自社HP/紹介/現地看板)"], note: "仮説シート・報告書ヒアリング項目「反響はどこから来ますか」に対応" },
    { id: "n46", block: "b8", lane: "eigyo", name: "反響者に電話で一次返信し内覧案内・追客フォローする", trigger: "反響受信後", tool: "電話／LINE", input: "反響情報・内覧時のヒアリング結果", output: "内覧対応・追客記録", minutes: 90, freq: 4, redo: "反応が薄いと複数回フォローが発生", assumed: true },
    { id: "n47", block: "b8", lane: "eigyo", name: "価格改定を判断し全媒体を手作業で直す", trigger: "滞留・反響停滞(値下げ判断)", tool: "各媒体の管理画面＋FAX／メール一斉配信", input: "新価格", output: "更新済み各媒体", minutes: 60, freq: 1, redo: "媒体ごとの直し漏れが発生しうる(業界一般の指摘)", assumed: true, unknown: ["滞留日数アラートの有無", "値下げに踏み切る基準"], note: "事実: 所沢市東新井町は2025-12〜2026-07(約7ヶ月)価格更新の痕跡なく滞留(調査報告書4章)。仮説シート★「13〜14の滞留アラートが無い兆候」" },

    // ===== b9 売買契約・ローン =====
    { id: "n48", block: "b9", lane: "shacho", name: "買主と価格交渉・条件調整をする", trigger: "内覧後の購入意思表示", tool: "対面・電話", input: "買主希望条件", output: "条件合意", minutes: 60, freq: 1, assumed: true },
    { id: "n49", block: "b9", lane: "jimu", name: "重要事項説明書・売買契約書を作成する", trigger: "条件合意", tool: "Word(自社ひな形)＋調査資料", input: "物件概要・法規調査メモ・登記情報", output: "重説・契約書", minutes: 120, freq: 1, assumed: true },
    { id: "n50", block: "b9", lane: "shacho", name: "重要事項説明を行い契約を締結する", trigger: "契約書準備完了", tool: "対面(宅建士による重説)", input: "重説・契約書", output: "締結済み契約書", minutes: 90, freq: 1, note: "重説は宅建士の法的責任(仮説シート・業界一般ステップ15で明記。自動化対象外の領域)" },
    { id: "m1", block: "b9", lane: "ext_kokyaku", type: "money_in", name: "手付金 入金", money_in: { amount: "10%目安", from: "買主", condition: "売買契約締結" }, minutes: 0, freq: 1, assumed: true, unknown: ["手付金の実際の料率"], note: "新築分譲の手付金相場(業界一般ステップ15)からの仮置き。Lancasaの実額は未確認" },
    { id: "n51", block: "b9", lane: "ext_kokyaku", name: "買主が住宅ローンの本申込・審査を行う", trigger: "契約締結後", tool: "金融機関窓口", input: "契約書・買主属性", output: "ローン承認", minutes: 0, freq: 1, wait: "承認まで数週間", assumed: true },
    { id: "n52", block: "b9", lane: "jimu", name: "決済日程を金融機関・司法書士・買主と調整する", trigger: "ローン承認", tool: "電話", input: "決済希望日", output: "決済日確定", minutes: 40, freq: 1, wait: "関係者調整に数日", assumed: true },

    // ===== b10 決済・引渡・入金・アフター =====
    { id: "n53", block: "b10", lane: "koumu", name: "引渡前の完了検査・是正確認をする", trigger: "完了検査済証取得後", tool: "紙チェックリスト・現地", input: "検査済証・是正記録", output: "引渡可否判断", minutes: 90, freq: 1, assumed: true },
    { id: "n54", block: "b10", lane: "jimu", name: "引渡書類一式(確認済証・検査済証・保険証券等)をチェックリストで整える", trigger: "決済日確定", tool: "紙チェックリスト", input: "確認済証・検査済証・瑕疵保険証券・取扱説明書", output: "引渡書類一式", minutes: 60, freq: 1, assumed: true },
    { id: "n55", block: "b10", lane: "ext_kokyaku", name: "決済・所有権移転登記を行う", trigger: "決済日到来", tool: "銀行窓口・司法書士立会", input: "締結済み契約書・引渡書類", output: "登記完了", minutes: 0, freq: 1, assumed: true, external_cost: { amount: 100000, to: "司法書士", item: "所有権移転登記手数料(自社負担分)" }, unknown: ["登記費用の自社負担有無・金額"], note: "登記費用は通常買主負担だが自社が一部負担するケースを想定。実額・負担区分は未確認" },
    { id: "m2", block: "b10", lane: "ext_kokyaku", type: "money_in", name: "残代金 入金", money_in: { amount: "90%目安(残金)", from: "買主(住宅ローン実行)", condition: "決済・引渡・登記完了" }, minutes: 0, freq: 1, wait: "契約からローン実行まで数週間", assumed: true, unknown: ["残金の実際の料率・入金タイミング"], note: "新築分譲の一般的な手付・残金配分からの仮置き" },
    { id: "n56", block: "b10", lane: "eigyo", name: "他社仲介経由で成約した場合、仲介手数料を支払う", trigger: "決済完了", tool: "振込", input: "仲介手数料請求書", output: "振込完了", minutes: 15, freq: 1, assumed: true, external_cost: { amount: 1500000, to: "客付け仲介会社", item: "仲介手数料(片手)支払" }, unknown: ["浜崎2号棟が自社客付けか他社仲介経由か"], note: "事実: 客付け仲介業者への依存度が高い構造(調査報告書4章)。本ノードは他社仲介で成約した場合のみ発生する分岐で、自社客付けの場合は発生しない。報告書ヒアリング項目「買主は自社で見つけたお客さんと、仲介業者さんが連れてくるお客さん、どちらが多いですか」で★未確認" },
    { id: "n57", block: "b10", lane: "eigyo", name: "買主へ鍵・取扱説明書を渡し引渡を完了する", trigger: "決済完了", tool: "対面", input: "引渡書類一式・鍵", output: "引渡完了", minutes: 60, freq: 1 },
    { id: "n58", block: "b10", lane: "jimu", name: "顧客情報をアフター台帳に転記する", trigger: "引渡完了", tool: "Excel(顧客台帳)", input: "引渡書類・買主情報", output: "アフター台帳Excel", minutes: 20, freq: 1, assumed: true, unknown: ["アフター台帳の有無・形式"] },
    { id: "n59", block: "b10", lane: "eigyo", name: "不具合連絡を担当営業の携帯で受ける", trigger: "引渡後の不具合発生", tool: "電話(担当携帯)", input: "口頭", output: "記憶／メモ", minutes: 15, freq: 2, assumed: true, unknown: ["アフター受付が代表電話か担当携帯か"], note: "仮説シート★「担当携帯なら情報が個人に埋まっている典型」" },
    { id: "n60", block: "b10", lane: "koumu", name: "協力業者へ不具合対応を手配する", trigger: "不具合連絡受領", tool: "電話", input: "不具合内容", output: "業者手配", minutes: 20, freq: 2, assumed: true },
    { id: "n61", block: "b10", lane: "eigyo", name: "定期点検(3ヶ月/6ヶ月/1年等)の案内・実施をする", trigger: "引渡日から一定期間経過", tool: "電話／訪問", input: "点検スケジュール", output: "点検報告", minutes: 60, freq: 3, assumed: true, unknown: ["定期点検の実施有無・時期"], note: "業界一般では3ヶ月/6ヶ月/1年/2年/5年/10年が目安(出典: any-one.jp)。ランドスタイルの実施状況は未確認" }
  ],
  edges: [
    { from: "n1", to: "n2", label: "電話→FAX/メール" }, { from: "n2", to: "n3" }, { from: "n3", to: "n4" },
    { from: "n4", to: "n5" }, { from: "n5", to: "n6" }, { from: "n6", to: "n7" },
    { from: "n7", to: "n8", label: "回答待ち数日" }, { from: "n8", to: "n9" }, { from: "n9", to: "n10" },
    { from: "n10", to: "n11" }, { from: "n11", to: "n12" },
    { from: "n12", to: "n13" }, { from: "n13", to: "n14" },
    { from: "n14", to: "n15", label: "メール発注" }, { from: "n14", to: "n16", label: "メール発注" },
    { from: "n15", to: "n17" }, { from: "n16", to: "n17" }, { from: "n17", to: "n62" },
    { from: "n62", to: "n19" },
    { from: "n19", to: "n20", label: "メール返信" }, { from: "n20", to: "n21" }, { from: "n21", to: "n22" },
    { from: "n22", to: "n23", label: "郵送/FAX" }, { from: "n23", to: "n24" },
    { from: "n24", to: "n25", label: "FAX/紙" }, { from: "n25", to: "n26" }, { from: "n26", to: "n27", label: "LINE" },
    { from: "n27", to: "n28" }, { from: "n28", to: "n29", label: "遅延時のみ" }, { from: "n25", to: "n29" },
    { from: "n29", to: "n30" }, { from: "n30", to: "n31" },
    { from: "n31", to: "n32" }, { from: "n32", to: "n33" }, { from: "n33", to: "n34" },
    { from: "n34", to: "n35" }, { from: "n35", to: "n36" }, { from: "n36", to: "n37", label: "メール発注・納品数日" },
    { from: "n37", to: "n38" }, { from: "n38", to: "n39" },
    { from: "n39", to: "n40", label: "FAX一斉" }, { from: "n39", to: "n41", label: "メール一斉" },
    { from: "n39", to: "n42" }, { from: "n39", to: "n43" }, { from: "n39", to: "n44" },
    { from: "n40", to: "n45" }, { from: "n41", to: "n45" }, { from: "n42", to: "n45" }, { from: "n43", to: "n45" }, { from: "n44", to: "n45" },
    { from: "n45", to: "n46" }, { from: "n46", to: "n47", label: "滞留・反響停滞時のみ" }, { from: "n47", to: "n42", label: "再掲載" },
    { from: "n46", to: "n48" }, { from: "n48", to: "n49" }, { from: "n49", to: "n50" }, { from: "n50", to: "m1" },
    { from: "m1", to: "n51" }, { from: "n51", to: "n52", label: "ローン承認待ち数週間" }, { from: "n52", to: "n53" },
    { from: "n53", to: "n54" }, { from: "n54", to: "n55" }, { from: "n55", to: "m2" },
    { from: "m2", to: "n56", label: "他社仲介経由の場合のみ" }, { from: "m2", to: "n57" },
    { from: "n57", to: "n58" }, { from: "n58", to: "n59" }, { from: "n59", to: "n60" }, { from: "n58", to: "n61" }
  ]
};
