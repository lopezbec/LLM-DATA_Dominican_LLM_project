from pathlib import Path

QUORUM_PATTERNS = [
    "comprobación del cuórum",
    "comprobacion del cuorum",
    "comprobado el cuórum reglamentario",
    "comprobado el quorum reglamentario",
    "1. comprobación del cuórum",
    "2. comprobación del cuórum",
    "1.1. comprobación del cuórum",
    "1.1.comprobación del cuórum",
    "1.1. Comprobación del cuórum",


]

CLOSING_PATTERNS = [

    "el diputado presidente levantó esta sesión",
    "el diputado presidente levanto esta sesion",
    "el diputado presidente levantó la sesión",
    "el diputado presidente levanto la sesion",


    "la diputada presidenta levantó esta sesión",
    "la diputada presidenta levanto esta sesion",
    "la diputada presidenta levantó la sesión",
    "la diputada presidenta levanto la sesion",

    "el diputado presidente declaró cerrada esta sesión",
    "el diputado presidente declaro cerrada esta sesion",
    "el diputado presidente declaró cerrada la presente sesión",
    "el diputado presidente declaro cerrada la presente sesion",
    "el diputado presidente declaró cerrada esta sesión ordinaria",
    "el diputado presidente declaro cerrada esta sesion ordinaria",
    "el diputado presidente declaró cerrada la sesión",
    "el diputado presidente declaro cerrada la sesion",

    "la diputada presidenta declaró cerrada esta sesión",
    "la diputada presidenta declaro cerrada esta sesion",
    "la diputada presidenta declaró cerrada la presente sesión",
    "la diputada presidenta declaro cerrada la presente sesion",
    "la diputada presidenta declaró cerrada la sesión",
    "la diputada presidenta declaro cerrada la sesion",


    "levantó esta sesión ordinaria",
    "levanto esta sesion ordinaria",
    "levantó la sesión ordinaria",
    "levanto la sesion ordinaria",

    "siendo las",
    "siendo la ",
]


def is_leader_line(line: str) -> bool:

    s = line.strip().lower()

    if "." * 10 in s or "…" in s:
        return True

    allowed = set(".·- 0123456789")
    if s and all(ch in allowed for ch in s) and any(ch.isdigit() for ch in s):
        return True
    return False


def find_quorum_start(text: str) -> int:

    lines = text.splitlines(keepends=True)
    offset = 0
    best_idx = -1

    for line in lines:
        low = line.lower()

        if is_leader_line(line):
            offset += len(line)
            continue

        for pat in QUORUM_PATTERNS:
            if pat in low:
                best_idx = offset
                break

        if best_idx != -1:
            break

        offset += len(line)

    return best_idx


def find_closing_index(text: str) -> int:

    t_low = text.lower()
    best = -1
    for pat in CLOSING_PATTERNS:
        pos = t_low.rfind(pat)
        if pos > best:
            best = pos
    return best


def split_meta_cuerpo(text: str) -> tuple[str, str]:

    idx_quorum = find_quorum_start(text)

    if idx_quorum == -1:
        return text, ""

    idx_close = find_closing_index(text)

    if idx_close == -1 or idx_close <= idx_quorum:
        meta_before = text[:idx_quorum]
        body = text[idx_quorum:]


        body_lines = []
        meta_extra = []
        for line in body.splitlines(keepends=True):
            if is_leader_line(line):
                meta_extra.append(line)
            else:
                body_lines.append(line)
        body_clean = "".join(body_lines)
        meta = meta_before + "".join(meta_extra)

        if len(body_clean.strip()) < 80:
            return text, ""

        return meta.strip(), body_clean.strip()


    meta_before = text[:idx_quorum]
    body = text[idx_quorum:idx_close]
    meta_after = text[idx_close:]


    body_lines = []
    meta_moved = []
    for line in body.splitlines(keepends=True):
        if is_leader_line(line):
            meta_moved.append(line)
        else:
            body_lines.append(line)

    body_clean = "".join(body_lines)
    meta = meta_before + "".join(meta_moved) + meta_after

    if len(body_clean.strip()) < 80:
        return text, ""

    return meta.strip(), body_clean.strip()


def main():
    base_dir = Path(__file__).resolve().parents[1] / "CDD_MD"
    raw_dir = base_dir / "Raw"
    body_dir = base_dir / "Body"
    meta_dir = base_dir / "Meta"

    body_dir.mkdir(parents=True, exist_ok=True)
    meta_dir.mkdir(parents=True, exist_ok=True)

    print(f"Usando Raw: {raw_dir}")

    problemas = []


    raw_files = sorted(raw_dir.glob("*.md"))

    for path in raw_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        meta, body = split_meta_cuerpo(text)

        if not body.strip() or not meta.strip():
            problemas.append(path.name)

        (body_dir / path.name).write_text(body, encoding="utf-8")
        (meta_dir / path.name).write_text(meta, encoding="utf-8")

        print(f"✓ Procesado: {path.name}")

    if problemas:
        print("\n⚠ Archivos a revisar (sin split perfecto o sin cuerpo):")
        for name in problemas:
            print(f"   - {name}")

    print("\nListo ✅")


if __name__ == "__main__":
    main()
