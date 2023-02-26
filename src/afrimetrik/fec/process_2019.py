import logging
import os
from afrimetrik.fec.fec_processor import FecProcessor
import afrimetrik.fec.utils as utils
from pathlib import Path
from typing import List, Dict, Optional
import pdfplumber
import argparse
import progressbar
import codecs
import time
from unidecode import unidecode

FAILURE = "failure"
SUCCESS = "success"

PROFILE_DEFAULT_SCHEMA: dict = {
    "name": "",
    "phone": "",
    "email": "",
    "social_links": None,
}

CONTACT_DEFAULT_SCHEMA: dict = {
    "profile": PROFILE_DEFAULT_SCHEMA,
    "phones": [],
    "email": "",
}

COMPANY_DEFAULT_SCHEMA: dict = {
    "legal_name": "",
    "city": "",
    "state": "",
    "sectors": [],
    "address": "",
    "site_url": "",
    "contact": CONTACT_DEFAULT_SCHEMA,
}


class MissingFilename(RuntimeError):
    ...


class ProcessFEC2019(FecProcessor):
    def start_processing(self) -> Path:
        logging.info(f"Start processing file {self.filename}")
        try:
            return self._process_file()
        except Exception as e:
            logging.info(f"An error occured during processing {e}")
            self.status = {"error": e, "status": FAILURE}

    def _process_file(self):
        companies = self.extractor()
        parent_folder = Path(os.path.join(os.getcwd(), "generated"))
        destination_filename = Path(
            os.path.join(os.getcwd(), "generated", f"produced_{int(time.time())}.json")
        )
        if not parent_folder.exists():
            parent_folder.mkdir(parents=True)
        with codecs.open(destination_filename, "w", encoding='utf-8') as file:
            self.write_file_to_json(companies, file)
        self.status = {"status": SUCCESS}
        logging.info(f"End processing, destination file {destination_filename}")
        return destination_filename

    def get_status(self) -> dict:
        return self.status

    def _get_companies_from_tables(self, tables) -> List[List[str]]:
        valid_tables = []
        for table in tables:
            fc = lambda s: s or ""
            valid = [
                unidecode(" | ".join(filter(fc, lines)))
                for lines in table
                if "".join(filter(fc, lines))
            ]
            valid_tables = valid_tables + valid
            print(valid_tables)
            raise Exception("OOPS!")
        company = []
        companies = []
        for line in valid_tables:
            company.append(line)
            if "secteur" in line:
                companies.append(company)
                company = []
                continue
        return companies

    def _parse_companies(self, page, state: Optional[str]) -> list[COMPANY_DEFAULT_SCHEMA]:
        companies = []
        tables = page.extract_tables()
        raw_companies = self._get_companies_from_tables(tables)
        
        for raw in raw_companies:
            company_name = utils.parse_legal(raw)
            address = utils.parse_address(raw)
            profile = PROFILE_DEFAULT_SCHEMA
            contact = CONTACT_DEFAULT_SCHEMA
            if not company_name:
                continue
            company = {
                "legal_name": company_name,
                "city": utils.parse_city(raw),
                "state": state,
                "sectors": utils.parse_sectors(raw),
                "address": address if address not in utils.EXCLUDE_ADDRESS_KEYS else None,
                "site_url": utils.parse_webinfo(raw)[1],
                "contact": {
                    **contact,
                    "profile": {**profile, "name": utils.parse_contact_name(raw)},
                    "phones": utils.parse_phones(raw),
                    "email": utils.parse_webinfo(raw)[0],   
                },
            }
            companies.append(company)
        return companies

    def extractor(self) -> List[Dict]:
        companies = []
        with pdfplumber.open(self.filename) as pdf:
            pages = pdf.pages
            processing_progress_bar = progressbar.ProgressBar(max_value=len(pages))
            processing_progress_bar.widgets = (
                ["processing pages: "]
                + [progressbar.widgets.FileTransferSpeed(unit="pages"), " "]
                + processing_progress_bar.default_widgets()
            )
            processing_progress_bar.start()
            state = None
            for idx, page in enumerate(pages):
                processing_progress_bar.update(idx + 1)
                if idx <= self.start_page:
                    continue
                page_str = "".join([t["text"] for t in page.chars])
                if new_state := utils.parse_state(raw=page_str):
                    state = new_state
                if page_companies := self._parse_companies(page, state):
                    companies += page_companies
            processing_progress_bar.finish()
        return companies


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

    logging.basicConfig(level="INFO")
    if not args.filename:
        logging.info("Bad Argument, filename is missing")
        raise MissingFilename("Missing filename")

    filename = args.filename
    process2019 = ProcessFEC2019(filename=filename, start_page=51)
    process2019.start_processing()
