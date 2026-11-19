"""雙擊開啟 ppSR persistent 編輯器（不會出現主控台視窗）。"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True          # 「文件」資料夾可能禁止寫入 __pycache__
sys.path.insert(0, str(Path(__file__).resolve().parent))

from ppsr_editor.app import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
