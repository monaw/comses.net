from django.core.management import call_command
from django.core.management.base import BaseCommand

from allauth.socialaccount.models import SocialApp
from django.conf import settings
from wagtail.core.models import Site
from curator.invoke_tasks.util import confirm

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Reconfigure staging site: read SocialAuth tokens from config.ini and reconfigure Site objects"

    def handle(self, *args, **options):
        # restore staging site SocialApp client_id + secrets
        orcid = SocialApp.objects.get(provider='orcid')
        orcid.client_id = settings.ORCID_CLIENT_ID
        orcid.secret = settings.ORCID_CLIENT_SECRET
        orcid.save()

        github = SocialApp.objects.get(provider='github')
        github.client_id = settings.GITHUB_CLIENT_ID
        github.secret = settings.GITHUB_CLIENT_SECRET
        github.save()
        # set Django Site object metadata appropriately
        if confirm("Update staging Site objects and robots.txt? (y/n) "):
            site = Site.objects.first()
            site.site_name = 'CoMSES Net Staging Site'
            site.hostname = 'test.comses.net'
            site.save()
            logger.debug("saved wagtail site %s", site)
            # set up robots.txt to deny all
            call_command('setup_robots_txt', '--no-allow')
            logger.debug("setup staging robots.txt")
