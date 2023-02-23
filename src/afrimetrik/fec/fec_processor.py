from __future__ import annotations
import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, TextIO

class FecProcessor(ABC):
    def __init__(self, filename: Path):
        self.filename = filename

    @abstractmethod
    def start_processing(self) -> Path:
        ...

    @abstractmethod
    def extractor(self) -> List[Dict]:
        ...
    
    @abstractmethod
    def get_status(self) -> dict:
        ...
    
    def write_file_to_json(self, records: List[Dict], file: TextIO) -> None:
        line_to_writes = [json.dumps(record) for record in records]
        for line in line_to_writes:
            file.write(f"{line}\n") 