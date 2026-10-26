# folk.luau 分析筆記

## 結論（一句話）
`folk.luau` 是 lilac 包裝的 **jnkie.com 金鑰系統載入器**，金鑰通過後從 `cdn.jnkie.com` 下載真正的主程式（`../payload/jnkie_payload.lua`，Luraph v15.1，仍混淆）。
**主程式的原始碼沒有被還原。** 在離線沙盒裡，Luraph VM 會進入一個我無法離開的迴圈，原因未解。

## 流程（用執行器的 request 日誌確認）
1. `loadstring(game:HttpGet("https://lilac.su/folk.luau"))()` → 顯示 `lilac ~ key system` 視窗（放在 `gethui()`）
2. 輸入金鑰 → `POST api.jnkie.com/api/v1/whitelist/verifyOpen`
3. → `POST api.jnkie.com/api/v1/luascripts/delivery/<hash>?v=2&errors=text`
4. → `GET cdn.jnkie.com/<sha256>.lua`（1.2 MB 主程式）

## 外層（folk.luau，397914 B）
Femboy Obfuscator v16.3 → 壓縮資料 + 小型解碼器。解碼後得到兩段：
- 164214 B 的 Luraph VM 原始碼 → `../decoded/inner.luau`
- 277567 B 的位元組碼 buffer → `../decoded/data.bin`（以參數傳給 VM）
解碼時只把 `loadstring` 換成「記錄但不執行」的假函式。

## 內層（Luraph VM）
- 位元組碼是**惰性解密**、**就地自我修改**的：部分 opcode 會用 xorshift 金鑰流解開後面指令的運算元。**不能亂讀運算元陣列**（`__index` 會觸發解碼並改變共享狀態），只能讀該 opcode 處理函式本來就會讀的。
- 函式內有 3 份不同編號的解譯迴圈（多型）。我只分析了 `while true do local k,R=I[b];if k>=85 …`（第 38 號）。
- `optree.py` 把它的 opcode 分派樹攤開，印出任一 opcode 的處理函式。
- 輔助函式全是純函式：`y[96]=buffer.readi16, y[107]=readu32, y[48]=writei8, y[90]=writei32, y[49]=band, y[26]=bxor, y[103]=bor, y[113]=bnot, y[75]=rshift, y[28]=lshift, y[115]=table.create, y[13]=table.move, y[89]=table.pack, y[99]=unpack, y[60]=coroutine.wrap …`

## 卡住的迴圈（只在我的沙盒）
- 主函式取得 `Instance, Vector3, Vector2, CFrame, Random, identifyexecutor, islclosure, iscclosure` 後，約 9.1 萬條 VM 指令後進入週期為 104 條指令的迴圈。
- 迴圈 = 3 個狀態 `12→17→5→12` 的流程平坦化狀態機（狀態只由常數載入決定）+ 對 144,115 位元組 buffer 的偽隨機讀寫（readi16/readu32/writei8/writei32 + xor/shift/mod）。
- 暫存器快照：沒有計數器，沒有依賴資料的出口。所有被呼叫的函式都不依賴環境。
- 實測：官方 Luau + `-O2 --codegen` 跑滿 25 分鐘沒有結束；注入「Script timeout」錯誤只會讓整個程式結束，沒有被任何一層接住。
- **矛盾**：真實客戶端能跑完（使用者回報會卡「幾秒到幾十秒」後出現視窗）。原因未知。可能：多執行緒、執行器/引擎的外層錯誤處理、或我沒覆蓋的另外兩份解譯變體。

## 我說錯後來撤回的事（避免誤導）
- 曾推測「刻意卡死/惡意」→ **撤回**。實際執行顯示它是正常的金鑰系統，沒有證據證明惡意。
- 曾說「迴圈只是慢」→ 25 分鐘測試推翻。
- 曾說 `o` 是環境指紋 → 不是，它是 proto 常數。

## 工具與重現
- `make_trace.py log|pc`：從 `../decoded/` 重新產生沙盒追蹤腳本（需官方 Luau，建議 `timeout`）。
- `../third_party/Deobfuscator-Luraph-V15`：能辨識 payload 為 Luraph v15（信心 1.00），但需要作者的「修補版 Luau」(`build_luau.py`，倉庫未附)；用官方版時 600 秒無輸出被判定停滯。

## 安全提醒
- 不要經由自動化通道（如 MCP）啟動這支腳本：多次造成客戶端凍結。自己手動執行才正常。
- 金鑰不要貼在公開處。
