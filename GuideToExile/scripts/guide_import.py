# manage.py runscript guide_import
import collections
import logging
import re

import cfscrape
from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model

from GuideToExile import pob_import, build_guide, skill_tree
from GuideToExile.models import BuildGuide
from GuideToExile.settings import GUIDE_IMPORT_USERNAME, GUIDE_IMPORT_MAIL, GUIDE_IMPORT_PASSWORD

logger = logging.getLogger('guidetoexile')

CLASS_FORUM_SECTION_URLS = [
    'https://www.pathofexile.com/forum/view-forum/40',
    'https://www.pathofexile.com/forum/view-forum/marauder',
    'https://www.pathofexile.com/forum/view-forum/24',
    'https://www.pathofexile.com/forum/view-forum/436',
    'https://www.pathofexile.com/forum/view-forum/303',
    'https://www.pathofexile.com/forum/view-forum/41',
    'https://www.pathofexile.com/forum/view-forum/22',
]

PASTEBIN_URL_REGEX = re.compile(r'https://pastebin\.com/\w*')

skill_tree_service = skill_tree.SkillTreeService()


def run():
    if not BuildGuide.objects.count() == 0:
        return
    user = make_importing_user()
    urls = generate_urls()
    guides_data = []
    for url in urls:
        guides_data.extend(scrape_forum_section_page(url))

    for data in guides_data:
        make_new_guide(data, user)


def make_importing_user():
    user, created = get_user_model().objects.get_or_create(username=GUIDE_IMPORT_USERNAME, email=GUIDE_IMPORT_MAIL)
    if created:
        user.set_password(GUIDE_IMPORT_PASSWORD)
        user.save()
    return user


def make_new_guide(guide_details, user):
    if not BuildGuide.objects.filter(title=guide_details.title).exists():
        logger.info(f'Creating guide {guide_details.title=}')
        try:
            import_str = pob_import.import_from_pastebin(guide_details.pastebin_url)
            build_xml = pob_import.base64_to_xml(import_str)
            pob_details = pob_import.parse_pob_details(build_xml)
            guide = build_guide.create_build_guide(user.userprofile, pob_details, import_str, skill_tree_service,
                                                   guide_details.post_content, guide_details.title)
            build_guide.publish_guide(guide)
        except Exception as e:
            logger.info(e, exc_info=True)


guide_data = collections.namedtuple('GuideData', ['post_content', 'pastebin_url', 'title'])


def scrape_guide_thread(thread_url):
    logger.info(f'Scraping {thread_url=}')
    scraper = cfscrape.create_scraper()
    page = scraper.get(thread_url)
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find('table')
    post, post_info = table.find_all('td')[0:2]
    pastebin_url = find_pastebin_url(post)
    if not pastebin_url:
        return None
    author_name = parse_post_info(post_info)
    title = soup.find('h1').text.strip()

    post_content = f'''<p>
    <strong>
        This guide was auto-imported! <br/>
        Originally it was posted by {author_name} on PoE forum here:<br/>
        <a href="{thread_url}">{thread_url}</a>
    </strong
</p>'''

    return guide_data(post_content, pastebin_url, title)


def find_pastebin_url(post):
    content_tree = post.find('div', class_='content')
    match = PASTEBIN_URL_REGEX.search(str(content_tree))
    if match:
        pastebin_url = match.group()
        return pastebin_url
    return None


def parse_post_info(post_info):
    profile_span = post_info.find('span', class_='profile-link')
    author_name = profile_span.find('a').text.strip()
    return author_name


def scrape_forum_section_page(page_url):
    scraper = cfscrape.create_scraper()
    page = scraper.get(page_url)
    soup = BeautifulSoup(page.content, "html.parser")
    titles = soup.find_all('div', class_='title')
    threads_urls = ['https://www.pathofexile.com' + title.find('a').get('href') for title in titles]
    guides_data = [data for thread_url in threads_urls if (data := scrape_guide_thread(thread_url))]
    return guides_data


def generate_urls():
    urls = []
    for section in CLASS_FORUM_SECTION_URLS:
        urls.append(section)
        for i in range(1, 2):
            urls.append(f'{section}/page/{i}')
    return urls
