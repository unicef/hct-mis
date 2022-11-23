import logging
from typing import Any

from django.core.management import BaseCommand

from hct_mis_api.apps.core.flex_fields_importer import FlexibleAttributeImporter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "load flex fields attributes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            dest="file",
            action="store",
            nargs="?",
            default="./data/FlexibleAttributesInit.xlsx",
            type=str,
            help="file",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        file = options["file"]
        importer = FlexibleAttributeImporter()
        importer.import_xls(file)
        logger.debug(f"Imported flex field attributes from {file}")
