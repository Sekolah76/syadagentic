#!/usr/bin/env python3
"""checkpoint.py — Auto-backup + rollback untuk file penting (SYADAGENTIC v6.0).
Sebelum modifikasi file penting → backup .bak-TIMESTAMP + log.
Kalau rusak → rollback dari backup terakhir.
Pakai ini SEBELUM edit 9router DB, hermes config, memory, dll.
"""
import shutil, datetime, os, sys, glob

LOG = r"~/.backup-log.txt"
PROTECTED = [
    r"~/AppData/Roaming/9router/db/data.sqlite",
    r"~/AppData/Local/hermes/config.yaml",
    r"~/AppData/Local/hermes/memories/MEMORY.md",
    r"~/AppData/Local/hermes/memories/USER.md",
    r"~/.ssh/ssh-key",
]

def backup(path):
    if not os.path.exists(path):
        return None, "tidak ada"
    ts = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    bak = f"{path}.bak-{ts}"
    shutil.copy2(path, bak)
    with open(LOG, "a") as f:
        f.write(f"{ts} BACKUP {path}\n")
    return bak, "OK"

def list_backups(path):
    return sorted(glob.glob(path + ".bak-*"), key=os.path.getmtime, reverse=True)

def restore(path):
    """Restore file dari backup terakhir. Args: restore <path>"""
    baks = list_backups(path)
    if not baks:
        print(f"  NO backup utk {path}")
        return
    shutil.copy2(baks[0], path)
    with open(LOG, "a") as f:
        f.write(f"{datetime.datetime.now():%Y%m%d%H%M%S} RESTORE {path} <- {os.path.basename(baks[0])}\n")
    print(f"  RESTORED {path} dari {os.path.basename(baks[0])}")

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        print("Usage: checkpoint.py [backup-all | backup <path> | restore <path> | list <path>]")
        sys.exit(0)
    cmd = args[0]
    if cmd == "backup-all":
        for p in PROTECTED:
            b, s = backup(p)
            print(f"  {s}: {os.path.basename(p)} -> {os.path.basename(b) if b else 'N/A'}")
    elif cmd == "backup" and len(args) > 1:
        b, s = backup(args[1])
        print(f"  {s}: {b or args[1]}")
    elif cmd == "restore" and len(args) > 1:
        restore(args[1])
    elif cmd == "list" and len(args) > 1:
        for b in list_backups(args[1])[:5]:
            print(f"  {os.path.basename(b)} ({os.path.getmtime(b):.0f})")