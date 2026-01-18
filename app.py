from flask import Flask, render_template, request, send_file
import pandas as pd
import io
import msoffcrypto
import os
from datetime import datetime

application = Flask(__name__)

@application.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_pass = request.form.get('password', '').strip()
        file = request.files.get('file')
        
        if not file or file.filename == '':
            return '<h3>未選擇檔案</h3>'

        try:
            # --- 自動解密邏輯 ---
            decrypted_file = io.BytesIO()
            office_file = msoffcrypto.OfficeFile(file)
            
            try:
                # 使用使用者輸入的密碼解密
                office_file.load_key(password=user_pass)
                office_file.decrypt(decrypted_file)
            except Exception:
                return f"<h3>解密失敗</h3><p>密碼 {user_pass} 錯誤或檔案未加密。</p>"
            
            decrypted_file.seek(0)
            
            # --- 讀取資料 ---
            # 優先嘗試 Excel，若失敗嘗試 HTML (蝦皮常用格式)
            try:
                df = pd.read_excel(decrypted_file)
            except:
                decrypted_file.seek(0)
                dfs = pd.read_html(decrypted_file, flavor='bs4')
                df = dfs[0] if dfs else None

            if df is None:
                return "<h3>檔案解析失敗</h3><p>解密成功但無法讀取表格內容。</p>"

            # --- 資料清洗與過濾 ---
            df.columns = [str(col).strip().replace('\n', '') for col in df.columns]
            
            # 設定你想保留的標題
            keep = ["訂單編號", "日期", "金額", "Y欄標題", "數量", "AT欄標題", "包裹號碼"]
            found_cols = [c for c in keep if c in df.columns]
            
            if not found_cols:
                return f"<h3>找不到指定欄位</h3><p>檔案現有欄位：{df.columns.tolist()}</p>"
            
            df = df[found_cols].drop_duplicates(subset="訂單編號", keep="first")
            
            # --- 輸出結果 ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False)
            output.seek(0)
            
            return send_file(output, as_attachment=True, download_name=f"整理完成_{datetime.now().strftime('%m%d')}.xlsx")

        except Exception as e:
            return f"<h3>系統錯誤</h3><p>{str(e)}</p>"

    return render_template('index.html')

if __name__ == "__main__":
    # Render 會透過環境變數指定 Port
    port = int(os.environ.get("PORT", 5000))
    application.run(host='0.0.0.0', port=port)