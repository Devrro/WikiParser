import bs4.element
import requests
import re

from bs4 import BeautifulSoup
from constants.html_constants import PATTERN_HREF, PATTERN_TITLE, PATTERN_CSS, PATTERN_ID


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', str(text)))


def has_technical_text(text, patterns):
    filtered = []
    for pattern in patterns:
        filtered.append(
            re.search(pattern, str(text))
        )
    return any(filtered)


class PageSoup:
    def __init__(self, page_url_name: str) -> None:
        self.page_title = None
        self.page = None
        self.page_url_name = page_url_name
        self.wiki_base_page_url = "https://uk.wikipedia.org"
        self.page_content = "bodyContent"
        self.list_of_filtered_css_classes = PATTERN_CSS
        self.filter_elements_by_ids = PATTERN_ID
        self.parse_url = self.get_parse_url()
        self.link_list = self.get_url_list()

    def get_parse_url(self) -> str:
        if "/wiki/" in self.page_url_name:
            return self.wiki_base_page_url + self.page_url_name

        return self.wiki_base_page_url + "/wiki/" + self.page_url_name

    def get_url_list(self) -> list[bs4.element.Tag]:

        try:
            request_page = requests.get(self.parse_url)
        except requests.RequestException:
            print("***ERROR***")
            return []

        page_parse = self.filter_bodies_content(request_page)
        list_of_tag_a_objects = page_parse.find_all(self.filter_links_from_soup)
        return list_of_tag_a_objects[:200]

    def filter_bodies_content(
            self,
            page_to_filter,
            page_content_id: str = None,
            filter_elements_by_ids: list[str] = None
    ):
        if not filter_elements_by_ids:
            filter_elements_by_ids = self.filter_elements_by_ids

        if not page_content_id:
            page_content_id = self.page_content

        page_parse = BeautifulSoup(page_to_filter.content, "html.parser")
        self.page = page_parse
        try:
            self.page_title = page_parse.find(id="firstHeading").span.text
        except AttributeError:
            print('NoneType object has no attribute text')
        page_parse = page_parse.find(id=page_content_id)

        for filtered_element in filter_elements_by_ids:
            decompose_element = page_parse.find(id=filtered_element)
            if decompose_element:
                try:
                    decompose_element.decompose()
                except TypeError:
                    print("Something went terribly wrong")

        return page_parse

    def filter_links_from_soup(self, tag):

        if tag.name != "a":
            return False

        filtered_class = True

        has_attr_class = tag.get("class")
        if has_attr_class:
            if any([
                css_cls in self.list_of_filtered_css_classes
                for css_cls in has_attr_class
            ]):
                return False

        has_href = tag.get("href")

        if not has_href:
            return False

        title = tag.get('title')

        if has_technical_text(has_href, PATTERN_HREF):
            return False

        if has_technical_text(title, PATTERN_TITLE):
            return False

        # Because we are parsing Ukrainian wiki I restrict pages with non-cyrillic title to search
        if not has_cyrillic(title):
            return False

        return filtered_class

    @staticmethod
    def convert_list_of_bs4_to_dicts(
            tags: list[bs4.element.Tag]
    ) -> list[dict]:
        return [PageSoup.convert_bs4_to_dict(tag) for tag in tags]

    @staticmethod
    def convert_bs4_to_dict(tag: bs4.element.Tag):
        return {
            "title": tag.get("title", None),
            "link": tag.get("href", None),
            "text": tag.get("text", None),
        }

    def __repr__(self):
        return f"Node: {self.__str__()}"

    def __str__(self):
        return f"{self.page_title}, links: {len(self.link_list)}"
