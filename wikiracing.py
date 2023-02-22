from time import sleep
from typing import List
from page_soup import PageSoup
from wikiped_link_instance import LinkNode


class WikiRacer:

    def __init__(
            self,
            max_redirects: int = 10_000,
            links_per_page: int = 200,
            requests_per_minute: int = 100
    ) -> None:
        self.max_redirects = max_redirects
        self.requests_per_minute = requests_per_minute
        self.links_per_page = links_per_page

    def find_path(
            self,
            start: str,
            finish: str
    ) -> List[str]:
        start_url = PageSoup(start)
        end_url = PageSoup(finish)
        end_link_dict = end_url.page_to_node()

        queue = [LinkNode(**link) for link in start_url.urls]
        visited = []
        visited_links = []

        visited.append(
            start_url.page_to_node()
        )
        page_count = 0
        while len(visited) < self.max_redirects:
            current_link_node = queue.pop(0)
            if any(end_link_dict.get("title") == link.title for link in queue):
                print("YASSSSSSSSSSSSSs")
                break
            sleep(self.requests_per_minute / 60)
            print(current_link_node.title)

            page_count += 1
            if page_count % 10 == 0:
                print(len(queue))
                print(len(visited))

            new_links_soup = PageSoup(current_link_node.link).urls
            new_links = [
                LinkNode(**link) for link
                in new_links_soup if link.get("link") not in visited_links
            ]
            break
            queue.extend(new_links)
            visited.append(current_link_node)
            visited_links.append(current_link_node.link)


find = WikiRacer()
find.find_path("Дружба", "Польська мова")
