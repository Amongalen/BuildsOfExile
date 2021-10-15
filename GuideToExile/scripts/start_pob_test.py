# manage.py runscript start_pob_test
import logging

from GuideToExile import pob_import

logger = logging.getLogger('guidetoexile')


def run():
    pastebin_url = 'https://pastebin.com/Q8KpdjfY'
    import_str = pob_import.import_from_pastebin(pastebin_url)
    build_xml = pob_import.base64_to_xml(import_str)
    pob_details = pob_import.parse_pob_details(build_xml)
    logger.info('success !!!')
