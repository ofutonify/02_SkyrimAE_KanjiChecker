import streamlit as st
from lxml import etree
from collections import defaultdict
import tempfile
import os

# ページ設定
st.set_page_config(
    page_title="02_AE_KanjiChecker",
    page_icon="🔍"
)

# --- フォントリスト読込（実行ファイルのある場所基準にする） ---
base_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(base_dir, "SkyrimAE_JP_BookFont.txt"), encoding="utf-8") as f:
    book = set(f.read())
with open(os.path.join(base_dir, "SkyrimAE_JP_EveryFont.txt"), encoding="utf-8") as f:
    every = set(f.read())
with open(os.path.join(base_dir, "SkyrimAE_JP_HandWriteFont.txt"), encoding="utf-8") as f:
    hand = set(f.read())

# --- CSS（デザイン・ダークモード・中央揃え・角丸・メイリオ）---
st.markdown("""
    <style>
    body { font-family: 'Meiryo', sans-serif; background: #f3f3f3; }
    .block-container { align-items: center; text-align: center; }
    .uploadbox, .resultbox { background: #efefef; border-radius: 20px; padding: 30px 10px; margin: 20px auto; width: 80%; }
    .resultbox { background: #d9d9d9; min-height: 120px; font-size: 1.1em; }
    .stButton > button { background: #d9d9d9; border-radius: 10px; font-size: 1.2em; padding: 10px 40px;}
    @media (prefers-color-scheme: dark) {
      body { background: #232323; color: #e0e0e0; }
      .uploadbox, .resultbox { background: #343434 !important; color: #e0e0e0 !important; }
      .stButton > button { background: #444444 !important; color: #e0e0e0 !important; }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("## 02 SkyrimAE KanjiChecker")
st.markdown("### 漢字・記号チェッカー")
st.markdown(
    "読み込んだ.xml、.ini、.txtに\nSkyrimAEバニラで表示されない<br>文字・漢字・記号があるかチェックするツールです"
    "<br>※ファイル1つにつき1回チェックできます<br>",
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader(
    "▼ここにファイルをドロップ",
    type=["xml", "txt", "ini"],
    key="kanji_file"
)

if uploaded_file:
    st.markdown(f"##### ファイル名: {uploaded_file.name}")

    # --- チェック開始ボタン ---
    if st.button("チェック開始", key="checkbtn"):
        ext = os.path.splitext(uploaded_file.name)[1].lower()
        font_to_ng = defaultdict(list)

        if ext == ".xml":
            # 一時ファイル化
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tf:
                tf.write(uploaded_file.read())
                temp_path = tf.name
            try:
                tree = etree.parse(temp_path)
                root = tree.getroot()
                for s in root.xpath("//String"):
                    rec = s.findtext("REC")
                    dest = s.findtext("Dest") or ""
                    if rec == "BOOK:FULL":
                        font_label = "EveryFont"
                        valid = every
                    elif rec == "BOOK:DESC":
                        if "$Handwritten" in dest:
                            font_label = "HandwriteFont"
                            valid = hand
                        else:
                            font_label = "BookFont"
                            valid = book
                    else:
                        font_label = "EveryFont"
                        valid = every
                    for ch in dest:
                        if ch not in valid and ch not in [' ', '　']:
                            font_to_ng[font_label].append(ch)
            finally:
                os.remove(temp_path)  # 判定後に削除

        elif ext in [".txt", ".ini"]:
            # txt/iniはストリーム直接
            lines = uploaded_file.read().decode("utf-8").splitlines()
            for line in lines:
                for ch in line.strip():
                    if ch not in every and ch not in [' ', '　']:
                        font_to_ng["EveryFont"].append(ch)
        else:
            st.error("⚠️ .xml, .txt, .ini 以外のファイル形式には対応していません")

        # --- 結果表示 ---
        result_text = ""
        for font in ["EveryFont", "BookFont", "HandwriteFont"]:
            chars = sorted(set(font_to_ng.get(font, [])))
            if chars:
                result_text += f"{font} → {' '.join(chars)}\n"
            else:
                result_text += f"{font} → （該当なし）\n"
        st.markdown(f'<div class="resultbox">{result_text.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="resultbox">ここに結果が表示されます</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="resultbox">ここに結果が表示されます</div>', unsafe_allow_html=True)
