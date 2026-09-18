"""
Temp & Prefetch Cleaner
------------------------
A simple Windows utility with a GUI to scan and clean:
  - %TEMP% (user temp folder)
  - C:\\Windows\\Temp (system temp folder)
  - C:\\Windows\\Prefetch (prefetch cache)

Run with:  python temp_cleaner.py
(Windows only. For best results with Prefetch, run as Administrator.)
"""

import os
import sys
import ctypes
import shutil
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def is_admin() -> bool:
    """Check if the script is running with administrator privileges (Windows)."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


def get_target_folders():
    """Return the list of (label, path) folders this tool targets."""
    temp_env = os.environ.get("TEMP") or os.environ.get("TMP") or ""
    windir = os.environ.get("WINDIR", r"C:\Windows")

    folders = [
        ("User Temp (%TEMP%)", temp_env),
        ("System Temp", os.path.join(windir, "Temp")),
        ("Prefetch", os.path.join(windir, "Prefetch")),
    ]
    # Only keep folders that actually exist
    return [(label, path) for label, path in folders if path and os.path.isdir(path)]


def human_size(num_bytes: float) -> str:
    """Convert a byte count into a human-readable string."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024.0:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.2f} PB"


def walk_files(folder):
    """Yield full file paths under folder (top-level files and files in subfolders)."""
    for root, dirs, files in os.walk(folder):
        for f in files:
            yield os.path.join(root, f)


# ----------------------------------------------------------------------
# Main Application
# ----------------------------------------------------------------------

class CleanerApp(tk.Tk):
    BG = "#1e1f26"
    CARD = "#2a2c38"
    ACCENT = "#5b8def"
    ACCENT_HOVER = "#4a7bd8"
    DANGER = "#e0575b"
    TEXT = "#f0f0f5"
    SUBTEXT = "#9a9cad"
    GREEN = "#59c97e"

    def __init__(self):
        super().__init__()
        self.title("Temp & Prefetch Cleaner")
        self.geometry("620x560")
        self.minsize(560, 500)
        self.configure(bg=self.BG)

        self.scanned_files = []          # list of full file paths found
        self.total_size = 0              # bytes
        self.folder_breakdown = {}       # label -> (count, size)
        self.is_busy = False

        self._build_style()
        self._build_ui()
        self._log(f"Ready. Running as administrator: {'Yes' if is_admin() else 'No'}")
        if not is_admin():
            self._log("Tip: run as Administrator for full access to Prefetch files.")

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------
    def _build_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "Horizontal.TProgressbar",
            troughcolor=self.CARD,
            background=self.ACCENT,
            bordercolor=self.CARD,
            lightcolor=self.ACCENT,
            darkcolor=self.ACCENT,
            thickness=14,
        )

    def _build_ui(self):
        # Header
        header = tk.Frame(self, bg=self.BG)
        header.pack(fill="x", padx=24, pady=(20, 10))

        tk.Label(
            header, text="🧹 Temp & Prefetch Cleaner",
            font=("Segoe UI", 18, "bold"), fg=self.TEXT, bg=self.BG
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Scans %TEMP%, Windows\\Temp, and Prefetch — review before you clean.",
            font=("Segoe UI", 10), fg=self.SUBTEXT, bg=self.BG
        ).pack(anchor="w", pady=(2, 0))

        # Stats card
        stats_card = tk.Frame(self, bg=self.CARD)
        stats_card.pack(fill="x", padx=24, pady=10)

        self.stat_files_var = tk.StringVar(value="—")
        self.stat_size_var = tk.StringVar(value="—")

        self._build_stat(stats_card, "Files found", self.stat_files_var, 0)
        self._build_stat(stats_card, "Total size", self.stat_size_var, 1)

        # Breakdown list
        self.breakdown_frame = tk.Frame(self, bg=self.BG)
        self.breakdown_frame.pack(fill="x", padx=24, pady=(0, 10))

        # Progress bar + status
        progress_frame = tk.Frame(self, bg=self.BG)
        progress_frame.pack(fill="x", padx=24, pady=(6, 4))

        self.progress = ttk.Progressbar(
            progress_frame, mode="determinate", style="Horizontal.TProgressbar"
        )
        self.progress.pack(fill="x")

        self.status_var = tk.StringVar(value="Idle")
        tk.Label(
            progress_frame, textvariable=self.status_var,
            font=("Segoe UI", 9), fg=self.SUBTEXT, bg=self.BG
        ).pack(anchor="w", pady=(4, 0))

        # Buttons
        btn_frame = tk.Frame(self, bg=self.BG)
        btn_frame.pack(fill="x", padx=24, pady=(10, 6))

        self.scan_btn = self._make_button(
            btn_frame, "🔍 Scan", self.ACCENT, self.on_scan
        )
        self.scan_btn.pack(side="left", padx=(0, 10))

        self.clean_btn = self._make_button(
            btn_frame, "🗑️ Clean Now", self.DANGER, self.on_clean
        )
        self.clean_btn.pack(side="left")
        self.clean_btn.configure(state="disabled")

        # Log box
        log_label = tk.Label(
            self, text="Activity Log", font=("Segoe UI", 10, "bold"),
            fg=self.TEXT, bg=self.BG
        )
        log_label.pack(anchor="w", padx=24, pady=(14, 2))

        log_frame = tk.Frame(self, bg=self.CARD)
        log_frame.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self.log_box = tk.Text(
            log_frame, bg=self.CARD, fg=self.SUBTEXT, insertbackground=self.TEXT,
            relief="flat", font=("Consolas", 9), wrap="word", state="disabled"
        )
        scrollbar = ttk.Scrollbar(log_frame, command=self.log_box.yview)
        self.log_box.configure(yscrollcommand=scrollbar.set)
        self.log_box.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        scrollbar.pack(side="right", fill="y")

    def _build_stat(self, parent, label, var, col):
        frame = tk.Frame(parent, bg=self.CARD)
        frame.grid(row=0, column=col, sticky="nsew", padx=20, pady=16)
        parent.grid_columnconfigure(col, weight=1)

        tk.Label(
            frame, text=label, font=("Segoe UI", 9), fg=self.SUBTEXT, bg=self.CARD
        ).pack(anchor="w")
        tk.Label(
            frame, textvariable=var, font=("Segoe UI", 20, "bold"),
            fg=self.TEXT, bg=self.CARD
        ).pack(anchor="w")

    def _make_button(self, parent, text, color, command):
        btn = tk.Button(
            parent, text=text, command=command,
            bg=color, fg="white", activebackground=color,
            font=("Segoe UI", 10, "bold"), relief="flat",
            padx=18, pady=8, cursor="hand2", bd=0
        )
        return btn

    def _render_breakdown(self):
        for w in self.breakdown_frame.winfo_children():
            w.destroy()

        for label, (count, size) in self.folder_breakdown.items():
            row = tk.Frame(self.breakdown_frame, bg=self.BG)
            row.pack(fill="x", pady=2)
            tk.Label(
                row, text=f"• {label}", font=("Segoe UI", 9),
                fg=self.TEXT, bg=self.BG, anchor="w"
            ).pack(side="left")
            tk.Label(
                row, text=f"{count} files — {human_size(size)}",
                font=("Segoe UI", 9), fg=self.SUBTEXT, bg=self.BG, anchor="e"
            ).pack(side="right")

    def _log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_busy(self, busy: bool, status: str = ""):
        self.is_busy = busy
        state = "disabled" if busy else "normal"
        self.scan_btn.configure(state=state)
        self.clean_btn.configure(state=state if self.scanned_files else "disabled")
        if status:
            self.status_var.set(status)

    # ------------------------------------------------------------------
    # Scan
    # ------------------------------------------------------------------
    def on_scan(self):
        if self.is_busy:
            return
        self._set_busy(True, "Scanning...")
        self.progress.configure(mode="indeterminate")
        self.progress.start(12)
        self._log("Starting scan...")
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self):
        folders = get_target_folders()
        found_files = []
        breakdown = {}
        total = 0

        for label, path in folders:
            count = 0
            size = 0
            try:
                for fpath in walk_files(path):
                    try:
                        fsize = os.path.getsize(fpath)
                    except OSError:
                        fsize = 0
                    found_files.append(fpath)
                    count += 1
                    size += fsize
            except Exception as e:
                self.after(0, self._log, f"Could not fully scan {label}: {e}")
            breakdown[f"{label}  ({path})"] = (count, size)
            total += size

        self.scanned_files = found_files
        self.total_size = total
        self.folder_breakdown = breakdown

        self.after(0, self._scan_done)

    def _scan_done(self):
        self.progress.stop()
        self.progress.configure(mode="determinate", value=0)
        self.stat_files_var.set(f"{len(self.scanned_files):,}")
        self.stat_size_var.set(human_size(self.total_size))
        self._render_breakdown()
        self._log(f"Scan complete: {len(self.scanned_files):,} files, {human_size(self.total_size)} total.")
        self._set_busy(False, "Scan complete. Review results, then Clean Now.")
        if self.scanned_files:
            self.clean_btn.configure(state="normal")

    # ------------------------------------------------------------------
    # Clean
    # ------------------------------------------------------------------
    def on_clean(self):
        if self.is_busy or not self.scanned_files:
            return

        confirm = messagebox.askyesno(
            "Confirm Cleanup",
            f"Delete {len(self.scanned_files):,} files "
            f"({human_size(self.total_size)}) from Temp/Prefetch?\n\n"
            "Files currently in use will be safely skipped.",
        )
        if not confirm:
            return

        self._set_busy(True, "Cleaning...")
        self.progress.configure(mode="determinate", value=0, maximum=len(self.scanned_files))
        self._log("Starting cleanup...")
        threading.Thread(target=self._clean_worker, daemon=True).start()

    def _clean_worker(self):
        deleted_count = 0
        deleted_size = 0
        skipped_count = 0
        total = len(self.scanned_files)

        for i, fpath in enumerate(self.scanned_files, start=1):
            try:
                fsize = os.path.getsize(fpath)
                os.remove(fpath)
                deleted_count += 1
                deleted_size += fsize
            except Exception:
                skipped_count += 1

            if i % 25 == 0 or i == total:
                self.after(0, self._update_clean_progress, i, total, deleted_count, skipped_count)

        # Try to remove now-empty subdirectories
        for label, path in get_target_folders():
            self._remove_empty_dirs(path)

        self.after(0, self._clean_done, deleted_count, deleted_size, skipped_count)

    def _update_clean_progress(self, i, total, deleted, skipped):
        self.progress.configure(value=i)
        self.status_var.set(f"Cleaning... {i}/{total} processed ({deleted} deleted, {skipped} skipped)")

    def _remove_empty_dirs(self, root_path):
        for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
            if dirpath == root_path:
                continue
            try:
                if not os.listdir(dirpath):
                    os.rmdir(dirpath)
            except Exception:
                pass

    def _clean_done(self, deleted_count, deleted_size, skipped_count):
        self._log(
            f"Cleanup complete: deleted {deleted_count:,} files "
            f"({human_size(deleted_size)}). Skipped {skipped_count:,} (in use or protected)."
        )
        self.status_var.set("Done. Run Scan again to refresh.")
        self.scanned_files = []
        self.total_size = 0
        self.stat_files_var.set("0")
        self.stat_size_var.set(human_size(deleted_size) + " freed")
        self.clean_btn.configure(state="disabled")
        self._set_busy(False)
        messagebox.showinfo(
            "Cleanup Complete",
            f"Deleted {deleted_count:,} files, freed {human_size(deleted_size)}.\n"
            f"Skipped {skipped_count:,} files that were in use."
        )


if __name__ == "__main__":
    if sys.platform != "win32":
        print("Warning: this tool targets Windows paths (%TEMP%, Windows\\Temp, Prefetch).")
    app = CleanerApp()
    app.mainloop()