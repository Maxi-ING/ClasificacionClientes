"""Descarga verificable del original de UCI, sin sobrescribirlo."""

import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile


def download_data(url: str, destination: Path) -> Path:
    """Extrae únicamente el XLSX esperado y registra su checksum."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    if not destination.exists():
        with urlopen(url, timeout=120) as response:
            archive = response.read()
        with ZipFile(io.BytesIO(archive)) as bundle:
            matches = [n for n in bundle.namelist() if Path(n).name == destination.name]
            if len(matches) != 1:
                raise ValueError("El ZIP debe contener un único archivo con el nombre esperado.")
            temporary = destination.with_suffix(".tmp")
            temporary.write_bytes(bundle.read(matches[0]))
            temporary.replace(destination)
    manifest = {
        "source": url,
        "file": destination.name,
        "bytes": destination.stat().st_size,
        "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
    }
    destination.with_suffix(".source.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    return destination
