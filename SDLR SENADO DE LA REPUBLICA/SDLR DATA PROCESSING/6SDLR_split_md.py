from pathlib import Path
import re


def split_metadata_body(text: str):
    """
    Separa:
      - metadata: encabezados, firmas, pies, etc.
      - body: desarrollo desde 'EN SANTO DOMINGO...' hasta antes de firmas/certificación.
    """
    patrones_inicio = [
        r'EN SANTO DOMINGO DE GUZMÁN',
        r'EN LA CIUDAD DE SANTO DOMINGO',
        r'EN SANTO DOMINGO, DISTRITO NACIONAL',
    ]

    start_idx = None
    for pat in patrones_inicio:
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            start_idx = m.start()
            break

    if start_idx is None:
        return text.strip(), ""

    m_end = re.search(
        r'FIRMAS BUFETE DIRECTIVO|FIRMAS SENADORES|FIRMAS RESPONSABLES DEL ACTA|CERTIFICACIÓN',
        text[start_idx:],
        re.IGNORECASE,
    )
    end_idx = start_idx + m_end.start() if m_end else len(text)

    metadata = (text[:start_idx] + text[end_idx:]).strip()
    body = text[start_idx:end_idx].strip()
    return metadata, body


def main():
    # carpeta donde está este script: .../SDLR DATA PROCESSING
    processing_dir = Path(__file__).resolve().parent

    # usamos el SDLR_MD que está DENTRO de SDLR DATA PROCESSING
    md_root = processing_dir / "SDLR_MD"
    raw_dir = md_root / "Raw"
    body_dir = md_root / "Body"
    meta_dir = md_root / "Meta"

    body_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    print(f"Usando Raw: {raw_dir}")

    # si quieres, aquí ves qué hay dentro
    for path in raw_dir.glob("*.md"):
        text = path.read_text(encoding="utf-8", errors="ignore")
        metadata_block, body_block = split_metadata_body(text)

        (body_dir / path.name).write_text(body_block, encoding="utf-8")
        (meta_dir / path.name).write_text(metadata_block, encoding="utf-8")

        print(f"✔ Procesado: {path.name}")

    print("Listo ✅")


if __name__ == "__main__":
    main()
