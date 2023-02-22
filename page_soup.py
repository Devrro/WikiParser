import requests
import re

from bs4 import BeautifulSoup


def has_cyrillic(text):
    return bool(re.search('[а-яА-Я]', str(text)))


technical_title_patterns = [
    "(Категорія:)",
    "(Спеціальна:)",
    "(Перегляд цього шаблону)",
    "(Редагувати розділ:)",
    "(Вікіпедія:)",
    "(Шаблон:)",
    "(Вікіпедія:Посилання на джерела)",
    "(Вікіпедія:Авторитетні джерела)",
    "(ще не написана)",
    "(q:Special)",
]

technical_href_patterns = [
    "cite_note",
    "cite_ref",
    "#Примітки",
]


def has_technical_text(text, patterns):
    filtered = []
    for pattern in patterns:
        filtered.append(
            re.search(pattern, str(text))
        )
    return any(filtered)


class PageSoup:
    def __init__(self, page_to_parse: str) -> None:
        self.page_title = None
        self.page = None
        self.page_to_parse = page_to_parse
        self.wiki_base_page_url = "https://uk.wikipedia.org"
        self.page_content = "bodyContent"
        self.list_of_filtered_css_classes = (
            "external",
            "mw-jump-link",
            "mw-disambig",
            "image",
            "internal",
            "mw-editsection-visualeditor",
            "wikiquote",
        )
        self.filter_elements_by_ids = [
            "toc", "contentSub", "Примітки"
        ]
        self.parse_url = self.get_parse_url()
        self.urls = self.get_link_nodes()

    def get_parse_url(self) -> str:

        if not self.page_to_parse:
            raise ValueError({
                "No page name were provided"
            })

        if "/wiki/" in self.page_to_parse:
            return self.wiki_base_page_url + self.page_to_parse
        return self.wiki_base_page_url + "/wiki/" + self.page_to_parse

    def get_link_nodes(self) -> list[dict]:
        try:
            request_page = requests.get(self.parse_url)
        except requests.RequestException:
            print("Request failed")
            return []
        page_parse = self.filter_bodies_content(request_page)
        list_of_tag_a_objects = page_parse.find_all(self.filter_links_from_soup)

        links = [
            self.convert_tag_to_node(
                a_tag_object, self.parse_url
            ) for a_tag_object
            in list_of_tag_a_objects
        ]

        return links

    def convert_tag_to_node(self, tag, prev=None):

        return {
            "link": tag.get("href", None),
            "title": tag.get("title", None),
            "text": tag.get("text", None),
            "prev_link": prev,
            "prev_title": self.page_title
        }

    def page_to_node(self):
        return {
            "title": self.page_title,
            "link": self.parse_url,
            "text": None,
            "prev_link": None,
            "prev_title": None,
        }

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
        self.page_title = page_parse.find(id="firstHeading").span.text
        page_parse = page_parse.find(id=page_content_id)

        for filtered_element in filter_elements_by_ids:
            decompose_element = page_parse.find(id=filtered_element)
            if decompose_element:
                try:
                    decompose_element.decompose()
                except Exception:
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

        if has_technical_text(has_href, technical_href_patterns):
            return False

        if has_technical_text(title, technical_title_patterns):
            return False

        # Because we are parsing Ukrainian wiki I restrict pages with non-cyrillic title to search
        if not has_cyrillic(title):
            return False

        return filtered_class

    def __repr__(self):
        return f"Node: {self.__str__()}"

    def __str__(self):
        return f"{self.page_title}, links: {len(self.urls)}"
