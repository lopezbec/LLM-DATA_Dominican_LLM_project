# 5SDLR_PDF-MD.py
from pathlib import Path
import datetime as dt
import unicodedata
import csv

import pdfplumber
from pdfplumber.utils.exceptions import PdfminerException

# Ubicaciones (este .py está en: SDLR DATA PROCESSING/)
ROOT_DIR = Path("../CDD ACTAS PDFS").resolve()
OUT_DIR  = Path("../CDD_MD/Raw").resolve()           # carpeta de salida con los .md
LOG_CSV  = OUT_DIR / "errores_pdf_md.csv"         # log de errores

OUT_DIR.mkdir(parents=True, exist_ok=True)

def norm(s: str) -> str:
    return unicodedata.normalize("NFC", (s or ""))

def pdf_to_md(pdf_path: Path, md_path: Path) -> tuple[bool, str]:
    """
    Devuelve (ok, motivo_error). ok=False si se debe saltar.
    """
    try:
        with pdfplumber.open(str(pdf_path)) as doc:
            pages = []
            for i, page in enumerate(doc.pages, start=1):
                txt = page.extract_text() or ""
                txt = norm(txt).strip()
                pages.append(txt if txt else f"[Página {i}: (sin texto extraíble)]")

            header = (
                f"# {pdf_path.stem}\n\n"
                f"- **Archivo origen:** `{pdf_path.as_posix()}`\n"
                f"- **Páginas:** {len(pages)}\n"
                f"- **Extraído:** {dt.datetime.now().isoformat(timespec='seconds')}\n\n"
            )

            md_path.parent.mkdir(parents=True, exist_ok=True)
            md_path.write_text(header + "\n\n---\n\n".join(pages) + "\n", encoding="utf-8")
        return True, ""
    except PdfminerException as e:
        # típico: PDF corrupto, no-PDF, cifrado sin clave, etc.
        return False, f"PdfminerException: {e}"
    except Exception as e:
        return False, f"Exception: {e.__class__.__name__}: {e}"

def main():
    total = 0
    ok = 0
    fails = []

    for pdf in sorted(ROOT_DIR.rglob("*.pdf")):
        total += 1
        rel = pdf.relative_to(ROOT_DIR)
        md_rel = rel.with_suffix(".md")
        md_path = OUT_DIR / md_rel

        success, err = pdf_to_md(pdf, md_path)
        if success:
            ok += 1
        else:
            fails.append((pdf.as_posix(), err))

    # Guardar log de errores (si hay)
    if fails:
        LOG_CSV.parent.mkdir(parents=True, exist_ok=True)
        with LOG_CSV.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.writer(f)
            w.writerow(["archivo_pdf", "motivo"])
            w.writerows(fails)

    # Resumen final
    print("✅ Conversión a Markdown finalizada")
    print(f"   Procesados: {total}")
    print(f"   OK:         {ok}")
    print(f"   Fallidos:   {len(fails)}")
    if fails:
        print(f"   🔎 Detalle de fallos en: {LOG_CSV}")

if __name__ == "__main__":
    main()
