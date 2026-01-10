import re
from pathlib import Path

DOCS_DIR = Path("docs_source")
MIN_CHARS = 80    # drop chunks shorter than this (too little to be useful)
MAX_CHARS = 1500  # split sections longer than this


def clean_markdown(text: str) -> str:
    # remove code-include lines like {* ../../docs_src/x.py *}
    text = re.sub(r"^\{\*.*\*\}\s*$", "", text, flags=re.MULTILINE)
    # remove note markers like "/// tip" and "///" (keeps the text inside)
    text = re.sub(r"^///.*$", "", text, flags=re.MULTILINE)
    # remove heading anchors like "{ #first-steps }"
    text = re.sub(r"\s*\{ #[^}]*\}", "", text)
    return text


def split_by_headings(text: str) -> list[dict]:
    sections = []
    heading = "Introduction"
    lines = []
    in_code = False

    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code  # entering or leaving a code block
        if not in_code and re.match(r"^#{1,3} ", line):
            sections.append({"heading": heading, "body": "\n".join(lines).strip()})
            heading = line.lstrip("#").strip()
            lines = []
        else:
            lines.append(line)

    sections.append({"heading": heading, "body": "\n".join(lines).strip()})
    return sections


def split_long(body: str) -> list[str]:
    if len(body) <= MAX_CHARS:
        return [body]
    pieces = []
    current = ""
    for paragraph in body.split("\n\n"):
        if current and len(current) + len(paragraph) > MAX_CHARS:
            pieces.append(current.strip())
            current = ""
        current += paragraph + "\n\n"
    if current.strip():
        pieces.append(current.strip())
    return pieces


def make_chunks(path: Path) -> list[dict]:
    text = clean_markdown(path.read_text(encoding="utf-8"))
    chunks = []
    for section in split_by_headings(text):
        if len(section["body"]) < MIN_CHARS:
            continue
        for piece in split_long(section["body"]):
            chunks.append(
                {
                    "id": f"{path.stem}_{len(chunks)}",
                    "text": f"{section['heading']}\n\n{piece}",
                    "source": path.name,
                    "heading": section["heading"],
                }
            )
    return chunks


def load_all_chunks() -> list[dict]:
    chunks = []
    for path in sorted(DOCS_DIR.glob("*.md")):
        chunks.extend(make_chunks(path))
    return chunks


if __name__ == "__main__":
    chunks = load_all_chunks()
    if not chunks:
        print("No chunks found. Is docs_source empty?")
        raise SystemExit
    lengths = [len(c["text"]) for c in chunks]
    print(f"Total chunks: {len(chunks)}")
    print(f"Shortest: {min(lengths)} chars, longest: {max(lengths)} chars")
    for c in chunks[:3]:
        print("-----")
        print(c["source"], "|", c["heading"])
        print(c["text"])