from time import sleep
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

    @staticmethod
    def trace_backward(
            node: LinkNode,
    ) -> list[str]:
        trace = []

        current_node = node
        while True:
            trace.insert(0, current_node.title)
            current_node = current_node.prev_link_node
            if current_node is None:
                break

        print(trace)
        return trace

    @staticmethod
    def create_end_nodes(page: PageSoup) -> LinkNode:
        return LinkNode(
            title=page.page_title,
            link=page.parse_url,
            text="",
            prev_link_node=None
        )

    def find_path(
            self,
            start: str,
            finish: str,
    ) -> list[str]:
        # pass
        start_page = PageSoup(start)
        end_page = PageSoup(finish)
        start_node = self.create_end_nodes(start_page)
        end_node = self.create_end_nodes(end_page)

        start_url_list = start_page.link_list
        start_url_dicts = PageSoup.convert_list_of_bs4_to_dicts(start_url_list)
        start_nodes = LinkNode.get_nodes_from_dicts(start_url_dicts, prev_node=start_node)

        queue = start_nodes
        visited = []
        visited_links = []

        visited.append(start_node)
        page_count = 0
        start_checked = False
        end_link_title = end_node.title

        if not start_checked:
            for node in queue:
                if node.title == end_link_title:
                    return self.trace_backward(node)
            start_checked = True
        while len(visited) < self.max_redirects:
            current_link_node = queue.pop(0)
            print(current_link_node.title)

            sleep(self.requests_per_minute / 60)

            page_count += 1

            if page_count % 10 == 0:
                print(len(queue))
                print(len(visited))

            new_page_soup = PageSoup(current_link_node.link)
            new_links_soup = new_page_soup.link_list

            url_dicts = PageSoup.convert_list_of_bs4_to_dicts(new_links_soup)
            new_nodes = []
            for url_dict in url_dicts:
                if url_dict.get('link') != current_link_node.link:
                    new_nodes.append(LinkNode.create_node_from_dict(url_dict, prev_link_node=current_link_node))

            if start_checked:
                for node in new_nodes:
                    if node.title == end_link_title:
                        return self.trace_backward(node)
                    queue.append(node)

            # for check_node in range(shift, len(queue)):
            #     if queue[check_node].title == end_link_title:
            #         return self.trace_backward(queue[check_node])

            visited.append(current_link_node)
            visited_links.append(current_link_node.link)


find = WikiRacer()
find.find_path("Марка (грошова одиниця)", "Китайський календар")
