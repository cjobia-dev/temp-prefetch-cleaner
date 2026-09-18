<div align="center">

# 🧹 Temp & Prefetch Cleaner

**A lightweight Windows GUI tool to safely clean `%TEMP%`, `Windows\Temp`, and `Prefetch`.**

![Platform](https://img.shields.io/badge/platform-Windows-0078D6?logo=windows&logoColor=white)
![Python](https://img.shields.io/badge/built%20with-Python%20%2B%20Tkinter-3776AB?logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)
![Release](https://img.shields.io/github/v/release/cjobia-dev/temp-prefetch-cleaner)

[Download](#-download) • [Features](#-features) • [Screenshots](#-screenshots) • [Usage](#-usage) • [Build from Source](#-build-from-source)

</div>

---

## 📖 About

Temp files and Prefetch cache quietly pile up on Windows over time, wasting disk space. **Temp & Prefetch Cleaner** gives you a simple, transparent way to see exactly how much clutter exists and remove it — no command line, no guesswork, no silently deleting things you didn't approve.

Scan first. Review the numbers. Clean when you're ready.

---

## ✨ Features

| | |
|---|---|
| 🔍 **Scan before you clean** | Nothing is deleted until you explicitly click Clean Now |
| 📊 **Live stats** | See total file count and total size, broken down per folder |
| 📈 **Progress bar** | Visual feedback while scanning and while deleting |
| 🛡️ **Crash-safe** | Locked or in-use files are automatically skipped, never forced |
| 📝 **Activity log** | Full transparency on what was deleted vs. skipped |
| ⚡ **Non-blocking UI** | Runs on a background thread — the window never freezes |

---

## 📥 Download

No Python installation needed — just grab the standalone executable:

**[⬇️ Download TempCleaner.exe (Latest Release)](https://github.com/cjobia-dev/temp-prefetch-cleaner/releases/latest)**

> ⚠️ Unsigned build — Windows SmartScreen may show a warning on first launch. Click **More info → Run anyway**.

---

## 🖥️ Screenshots

<div align="center">
<p align="center"> 
<img src="SCREENSHOT OF PROJECT/ss3.jpg" width="32%" /> 
<img src="SCREENSHOT OF PROJECT/ss2.jpg" width="32%" /> 
<img src="SCREENSHOT OF PROJECT/ss1.jpg" width="32%" /> 
</p>
</div>

---

## 🚀 Usage

1. Launch `TempCleaner.exe`
2. Click **Scan** — review the file count, total size, and per-folder breakdown
3. Click **Clean Now** and confirm
4. Watch the progress bar and activity log as it clears each folder

> 💡 For full access to the Prefetch folder, right-click the exe → **Properties → Compatibility → Run this program as an administrator.**

---

## 🛠️ Build from Source

```bash
git clone https://github.com/cjobia-dev/temp-prefetch-cleaner.git
cd temp-prefetch-cleaner
python temp_cleaner.py
```

**Requirements:** Windows 10/11, Python 3.8+

To build your own `.exe`:

```bash
pip install pyinstaller
python -m PyInstaller --onefile --windowed --name TempCleaner temp_cleaner.py
```

---

## ⚠️ Notes

- Windows only
- Only targets `%TEMP%`, `Windows\Temp`, and `Prefetch` — never touches Downloads, Recycle Bin, or other user files
- Use at your own risk; always review scan results before cleaning

---

<div align="center">

Made with 🐍 Python + Tkinter

</div>
