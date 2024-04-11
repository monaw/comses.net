from django.core.management.base import BaseCommand

from library.doi import register_peer_reviewed_codebases
from library.doi import (
    mona_test,
    mona_test_datacite_pkg,
    mona_test_request,
    mona_test_release,
)

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Mint DOIs for all peer reviewed codebase releases without a DOI"

    def handle(self, *args, **options):
        # logger.debug("Registering all peer reviewed codebases")
        codebases = register_peer_reviewed_codebases()
        # logger.debug("DOIs minted for %s", codebases)
        # mona_test()
        # mona_test_datacite_pkg()
        # mona_test_request()
        # mona_test_release()
