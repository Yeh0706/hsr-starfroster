<h1 align="center">Starfroster</h1>

<p align="center">
  ppSR <code>persistent.json</code> 編輯器<br>
  An editor for ppSR's <code>persistent.json</code>
</p>

<p align="center">
  <a href="https://github.com/Yeh0706/hsr-starfroster/releases">下載 Download</a> ·
  <a href="#繁體中文">繁體中文</a> ·
  <a href="#english">English</a>
</p>

---

## 繁體中文

Starfroster 是給 **ppSR** 使用的設定編輯器，用圖形介面修改 `misc\persistent.json`，不用再手動改 JSON。

### 功能

- **編隊**
  - 人數不限，可以超過 4 人
  - 同一角色可以重複加入
  - 拖曳或用 ↑↓ 調整順序
  - 選角視窗：頭像格狀排列，可搜尋名稱／ID／代號，依屬性、命途、星級篩選，支援多選
  - 開拓者、三月七只會顯示目前命途的那一位
  - 右鍵可以自訂角色顯示名稱
- **角色外觀**
  - 開拓者性別、命途（只列出遊戲裡真的有的命途），以及三月七命途；頭像會跟著命途切換
  - 皮膚：一個角色一行，用下拉選單選「預設」或皮膚，頭像會換成皮膚頭像
- **切換地圖**
  - 戰鬥（擬造花萼）／探索／測試服／我的收藏
  - 依世界分組、可搜尋；顯示目前位置，可以收藏
  - 傳送後一鍵「儲存並重啟 ppsr」
- **進階**：有語法上色和格式檢查的原始 JSON 編輯器
- **其他**
  - 標題列顯示 ppsr 是否在執行，可一鍵重啟 ppsr
  - 偵測檔案被外部修改
  - 存檔保留原本的換行格式
  - 介面語言：简体中文／English；預設深色主題（可改淺色或跟隨系統），強調色跟隨 Windows 輔色
  - 可在設定頁建立桌面／開始功能表捷徑

`global_passive`、`buff`、`send_hotfix`、`key`、`leader` 這些欄位不會出現在介面上，存檔時會原樣保留。

### 安裝與使用

1. 到 [Releases](https://github.com/Yeh0706/hsr-starfroster/releases) 下載 `Starfroster.zip`。
2. **先解壓縮**，再執行資料夾裡的 `Starfroster.exe`。`_internal` 資料夾必須跟 exe 放在一起。
3. 第一次開啟時，選擇 ppSR 的 `persistent.json`，通常在 `ppSR_REL_x.x.x\misc\persistent.json`。
4. 改完按「儲存」或 `Ctrl+S`。`persistent.json` 只會在 ppsr 啟動時讀取，所以要按標題列的「重啟 ppsr」，再重新登入遊戲。

> Windows Defender 可能會跳出警告，這是 PyInstaller 打包程式常見的誤判。按「其他資訊」→「仍要執行」即可。

### 資料存放位置

| 內容 | 位置 |
|---|---|
| 設定（語言、主題、檔案路徑） | `%APPDATA%\ppSR-persistent-editor\settings.json` |
| 自訂角色名稱、收藏地圖、資源快取 | ppSR 資料夾旁的 `persistent編輯器資料\` |

### 從原始碼執行

需要 Python 3.10 以上，在 Windows 上執行：

```bash
pip install -r requirements.txt
pythonw 啟動編輯器.pyw
```

---

## English

Starfroster is a settings editor for **ppSR**. It edits `misc\persistent.json` through a GUI, so you don't have to hand-edit the JSON.

### Features

- **Lineup**
  - Any number of characters, including more than 4
  - The same character can be added more than once
  - Reorder by drag and drop or the ↑↓ buttons
  - Character picker: portrait grid, search by name / ID / tag, filter by element, path and rarity, multi-select
  - Only the Trailblazer / March 7th of the current path is offered
  - Right-click a card to set a custom display name
- **Appearance**
  - Trailblazer gender and path (only paths that exist in the game data), and March 7th's path; the portrait follows the chosen path
  - Skins: one row per character with a "Default / skin" drop-down; the portrait switches to the skin's icon
- **Teleport**
  - Combat (Calyx) / Explore / Beta server / Favorites
  - Grouped by world and searchable; shows the current location, which you can add to favorites
  - "Save and restart ppsr" right after teleporting
- **Advanced**: raw JSON editor with syntax colors and validation
- **Other**
  - ppsr running status in the title bar and a one-click ppsr restart
  - Detects changes made to the file outside the editor
  - Saves keep the original line endings
  - UI language: Simplified Chinese / English; dark theme by default (light or system also available), accent color follows Windows
  - Create Desktop / Start menu shortcuts from Settings

Fields with no UI (`global_passive`, `buff`, `send_hotfix`, `key`, `leader`) are kept exactly as they are when saving.

### Install & use

1. Download `Starfroster.zip` from [Releases](https://github.com/Yeh0706/hsr-starfroster/releases).
2. **Extract it first**, then run `Starfroster.exe`. Keep the `_internal` folder next to the exe.
3. On first launch, choose ppSR's `persistent.json`, usually `ppSR_REL_x.x.x\misc\persistent.json`.
4. Click Save or press `Ctrl+S`. ppsr only reads `persistent.json` when it starts, so click "Restart ppsr" in the title bar and log in to the game again.

> Windows Defender may show a warning. This is a common false positive for PyInstaller apps. Click "More info" → "Run anyway".

### Where data is stored

| What | Where |
|---|---|
| Settings (language, theme, file path) | `%APPDATA%\ppSR-persistent-editor\settings.json` |
| Custom names, favorite maps, resource cache | `persistent編輯器資料\` next to the ppSR folder |

### Run from source

Requires Python 3.10+ on Windows:

```bash
pip install -r requirements.txt
pythonw 啟動編輯器.pyw
```

---

## 資料來源 / Credits

| 內容 Data | 來源 Source |
|---|---|
| 角色名稱、頭像 Character names & portraits | [nanoka.cc](https://hsr.nanoka.cc) |
| 命途圖示 Path icons | [Mar-7th/StarRailRes](https://github.com/Mar-7th/StarRailRes) |
| 皮膚頭像 Skin icons | [alioth.wiki](https://alioth.wiki) |
| 地圖資料 Map data (`scenes.json`) | [CAtlas0784/Escape-penacony](https://github.com/CAtlas0784/Escape-penacony) |
| 介面元件 UI components | [PySide6](https://doc.qt.io/qtforpython-6/) · [QFluentWidgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets) |

資料與圖片會在執行時下載並快取在本機，本倉庫不包含任何遊戲素材。
Data and images are downloaded and cached locally at runtime; this repository contains no game assets.

## 免責聲明 / Disclaimer

本專案為粉絲自製工具，與 HoYoverse 無關。《崩壞：星穹鐵道》相關的名稱、圖像與素材之著作權及商標權歸 HoYoverse 所有。
This is a fan-made tool and is not affiliated with HoYoverse. Honkai: Star Rail names, images and assets are trademarks and copyrights of HoYoverse.

## 授權 / License

Starfroster 的原始碼以 [MIT License](LICENSE) 釋出。
The Starfroster source code is released under the [MIT License](LICENSE).

打包後的程式包含 PySide6（LGPL-3.0）與 QFluentWidgets（GPL-3.0），這些元件適用各自的授權條款。
Packaged builds include PySide6 (LGPL-3.0) and QFluentWidgets (GPL-3.0), which remain under their own licenses.
