import os, sys, shutil, subprocess
from pathlib import Path
from tkinter import Tk, filedialog, messagebox

BITRATE = "192k"  # cambia a 128k/256k si quieres

def find_ffmpeg():
    # 1) Si está empacado con PyInstaller (--add-binary)
    try:
        meipass = Path(sys._MEIPASS)  # type: ignore[attr-defined]
        for name in ("ffmpeg.exe", "ffmpeg"):
            p = meipass / name
            if p.exists():
                return str(p)
    except Exception:
        pass
    # 2) Junto al .exe/.py
    base = Path(getattr(sys, "executable", __file__)).parent
    for name in ("ffmpeg.exe", "ffmpeg"):
        p = base / name
        if p.exists():
            return str(p)
    # 3) En el PATH del sistema
    return shutil.which("ffmpeg")

def convert(files, out_dir=None, bitrate=BITRATE):
    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        messagebox.showerror(
            "FFmpeg no encontrado",
            "No se encontró ffmpeg.\n\nOpciones:\n- Instálalo (winget/choco/brew)\n"
            "- O coloca ffmpeg* junto al .exe\n- O empaqueta con --add-binary"
        )
        return

    ok, fails = 0, []
    for src in files:
        try:
            src = str(src)
            base = os.path.splitext(os.path.basename(src))[0]
            dst_dir = out_dir or os.path.dirname(src)
            os.makedirs(dst_dir, exist_ok=True)
            dst = os.path.join(dst_dir, base + ".mp3")
            cmd = [ffmpeg, "-y", "-i", src, "-vn", "-acodec", "libmp3lame", "-b:a", bitrate, dst]
            creation = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
            subprocess.run(cmd, check=True, creationflags=creation)
            ok += 1
        except Exception as e:
            fails.append((src, str(e)))

    msg = f"Convertidos: {ok}\nFallidos: {len(fails)}"
    if fails:
        msg += "\n\nErrores:\n" + "\n".join(f"- {Path(p).name}: {err}" for p, err in fails)
    messagebox.showinfo("MP4 → MP3", msg)

if __name__ == "__main__":
    root = Tk(); root.withdraw()
    files = filedialog.askopenfilenames(
        title="Selecciona uno o más .mp4",
        filetypes=[("Videos MP4", "*.mp4")]
    )
    if not files:
        sys.exit(0)
    out_dir = filedialog.askdirectory(
        title="Carpeta de salida (opcional). Cancel = misma carpeta"
    ) or None
    convert(files, out_dir)
