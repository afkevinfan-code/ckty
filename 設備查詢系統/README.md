# 桃園智慧停車設備查詢系統

這是一個離線、本機使用的查詢網頁。路段代碼為必填，可再以車格編號或設備類別篩選，並顯示設備、車牌鏡頭、SIM、IP 與 PORT 資料。

## 使用方式

直接以瀏覽器開啟 `index.html` 即可使用。因資料檔已內嵌在網頁，不需要網路或伺服器。

## 更新來源資料

原始 Excel 更新後，在此資料夾執行：

```bash
/Users/kevinfan/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 update_data.py
```

此動作會由 `/Users/kevinfan/Desktop/桃園電池版設備明細表系統_v0626.xlsx` 重新產生 `data.js`。車格編號及數字型車牌序號會依 Excel 的顯示格式保留前導零；來源表內完全相同的重複列會自動合併，避免查詢結果重複顯示。

## 設備類別判讀

- 市電版自然排水：來源欄位 V
- 市電版電動排水：來源欄位 W
- 路緣石電池版（左／右／度數）：來源欄位 X:Y、AA:AB
- 電池版自然排水：來源欄位 AD
- 電池版電動排水：來源欄位 AE
