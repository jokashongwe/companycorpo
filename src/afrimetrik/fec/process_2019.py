import logging
import os
from afrimetrik.fec.fec_processor import FecProcessor
import afrimetrik.fec.utils as utils
from pathlib import Path
from typing import List, Dict, Optional
import pdfplumber
from pdfplumber.page import Page
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
    "name": "",
    "phones": [],
    "email": "",
}

FEC_CONSTANT = "REPERTOIRE DES ENTREPRISES COMMERCIALES, INDUSTRIELLES ET DE SERVICES"

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
            e.with_traceback()
            self.status = {"error": e, "status": FAILURE}

    def _process_file(self):
        companies = self.extractor()
        parent_folder = Path(os.path.join(os.getcwd(), "generated"))
        destination_filename = Path(
            os.path.join(os.getcwd(), "generated", f"produced_{int(time.time())}.json")
        )
        if not parent_folder.exists():
            parent_folder.mkdir(parents=True)
        with codecs.open(destination_filename, "w", encoding="utf-8") as file:
            self.write_file_to_json(companies, file)
        self.status = {"status": SUCCESS}
        logging.info(f"End processing, destination file {destination_filename}")
        return destination_filename

    def get_status(self) -> dict:
        return self.status

    def _get_companies_from_tables(
        self, page_text: str, state: str = ""
    ) -> List[List[str]]:
        tables = page_text.strip().split("\n")
        company = []
        companies = []
        taken = False
        for idx, line in enumerate(tables):
            line = line.strip()
            if line == FEC_CONSTANT:
                continue
            if taken:
                taken = False
                continue
            if len(line) < 3 or " " not in line:
                continue
            if "Tél" in line:
                parts = line.split("Tél")
                company = utils.append_to_company(company, parts[0].strip())
                company = utils.append_to_company(company, f"Tél{parts[1].replace('.', '').strip()}")
            elif utils.has_address(line):
                if address := utils.parse_address(line):
                    company = utils.append_to_company(company, address)
                if address:
                    other = line.replace(address, "").strip()
                    company = utils.append_to_company(company, other)
            elif "@" in line:
                parts = line.split(" ")
                last = parts[-1]
                if 'www' in last:
                    email = last.split('www')[0]
                    siteurl = last.split('www')[-1]
                    company = utils.append_to_company(company, email)
                    company = utils.append_to_company(company, f"www{siteurl}")
                else:
                    company = utils.append_to_company(company, last)
            else:
                company.append(line)

            if "description" in line.lower():
                if "www" in tables[idx] or "des" in tables[idx] or "et" in tables[idx]:
                    taken = True
                    company.append(f"{tables[idx]}")
                company = list(set(company))
                companies.append(company)
                company = []
        return companies

    def _parse_companies(
        self, page: Page, state: Optional[str]
    ) -> list[COMPANY_DEFAULT_SCHEMA]:
        companies = []
        page_text = page.extract_text()
        raw_companies = self._get_companies_from_tables(page_text, state=state)
        for raw in raw_companies:
            company_name = utils.parse_legal(raw)
            if not company_name:
                continue
            company = {
                "legal_name": company_name,
                "city": utils.parse_city(raw),
                "state": utils.parse_state(raw),
                "sectors": utils.parse_sectors(raw),
                "address": utils.parse_address(raw, company_name),
                "contact": {
                    "name": utils.parse_contact_name(raw),
                    "phones": utils.parse_phones(raw),
                    "email": utils.parse_webinfo(raw),
                    "site_url": utils.parse_siteurl(raw),
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
                if new_state := utils.parse_state(list_comp=page_str):
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
    process2019 = ProcessFEC2019(filename=filename, start_page=52)
    process2019.start_processing()
