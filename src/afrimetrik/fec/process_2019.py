import logging
import os
from afrimetrik.fec.fec_processor import FecProcessor
from pathlib import Path
from typing import List, Dict
import pdfplumber
import argparse

FAILURE = 'failure'
SUCCESS = 'success'

class MissingFilename(RuntimeError):
    ...

class ProcessFEC2019(FecProcessor):

    def start_processing(self) -> Path:
        logging.info(f"Start processing file {self.filename}")
        try:
            companies = self.extractor()
            destination_filename = Path(os.path.join(os.getcwd(), 'processed', '_produced.json'))
            with open(destination_filename) as file:
                self.write_file_to_json(companies, file)
            self.status = {'status': SUCCESS}
            return destination_filename
        except Exception as e:
            logging.info(f"An error occured during processing {e}")
            self.status = {'error': e, 'status': FAILURE}
    
    def get_status(self) -> dict:
        return self.status
    
    def extractor(self) -> List[Dict]:
        with pdfplumber.open(self.filename) as pdf:
            for page in pdf.pages:
                print(page.chars[0])

def __get_args_to_process() -> str:
    process_args: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Data source Argparser",
        add_help=False,
    )

    process_args.add_argument(
        "-f",
        "--filename",
        type=str,
        default=None,
        help="What is the filename",
    )

    return process_args.parse_args()

if __name__ == "__main__":
    args = __get_args_to_process()

    logging.basicConfig(level='INFO')
    if not args.filename:
        logging.info("Bad Argument, filename is missing")
        raise MissingFilename("Missing filename")
    
    filename = args.filename
    process2019 = ProcessFEC2019(filename=filename)
    process2019.start_processing()