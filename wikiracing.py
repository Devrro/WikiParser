from typing import List
from page_soup import PageSoup

requests_per_minute = 100
links_per_page = 200


class WikiRacer:
    queue = []
    visited = []

    def find_path(
            self,
            start: str,
            finish: str
    ) -> List[str]:
        start_node = {
            "link": "https://uk.wikipedia.org/" + "wiki/" + start,
            "title": start,
            "text": start,
            "prev": None,
            "prev_link": None,
        }
        start_url = PageSoup(start)
        end_url = PageSoup(finish)

        WikiRacer.visited.append(start_node)
        WikiRacer.queue.append(start_url.urls)
        # print(*start_urls, sep="\n")
        # while self.queue:
        #     self.queue.pop(0)

    def solve(self,):
        pass

find = WikiRacer()
find.find_path("Дружба", "Рим")
