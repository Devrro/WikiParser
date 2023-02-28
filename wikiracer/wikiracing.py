from time import sleep
from django.db.models import QuerySet

from wikiracer.page_soup import PageSoup
from wikiracer.wikiped_link_instance import LinkNode
from wikiracer_db.db_link_conn import DbLinkConnection
from wikiracer_db.models import LinkListWay, LinkObject, LinkRacerResult, LinkConnection

from django.db.models import ObjectDoesNotExist

from django.db.models import Max


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
    def save_racer_result(trace: list[str]) -> QuerySet[LinkListWay]:
        mark_up_index_links = len(trace)
        start_link = LinkObject.objects.get(title=trace[0])
        end_link = LinkObject.objects.get(title=trace[-1])

        end_points = DbLinkConnection.connect_points(
            start_link, end_link, LinkRacerResult
        )
        way_attempt_index = list(
            LinkListWay.objects.annotate(Max('way_attempt_index')).distinct().filter(end_points=end_points).values(
                "way_attempt_index"))[0]["way_attempt_index"]
        for index_in_way in range(mark_up_index_links):
            DbLinkConnection.save_path_to_db(
                way_attempt_index=way_attempt_index,
                end_points=end_points,
                list_index=index_in_way,
                link_object=LinkObject.objects.get(title=trace[index_in_way])
            )
        return LinkListWay.objects.filter(end_points=end_points)

    @staticmethod
    def create_end_nodes(page: PageSoup) -> LinkNode:
        return LinkNode(
            title=page.page_title,
            link=page.parse_url,
            text="",
            prev_link_node=None
        )

    @staticmethod
    def find_short_path_in_db(
            start: str,
            end: str,
    ) -> list[str]:
        try:
            start_link_object = LinkObject.objects.get(title__iexact=start)
            end_link_object = LinkObject.objects.get(title__iexact=end)
        except ObjectDoesNotExist:
            return []
        is_paired = LinkConnection.objects.filter(
            start_link=start_link_object,
            end_link=end_link_object
        ).exists()
        if is_paired:
            return [start_link_object.title, end_link_object.title]
        return []

    def find_path(
            self,
            start: str,
            finish: str,
    ) -> list[str]:
        # pass
        res = self.find_short_path_in_db(start, finish)
        if res:
            return res

        start_page = PageSoup(start)
        end_page = PageSoup(finish)

        start_node = self.create_end_nodes(start_page)
        end_node = self.create_end_nodes(end_page)

        if LinkObject.objects.filter(title=start_node.title).exists():
            start_link_object = LinkObject.objects.get(title=start_node.title)
        else:
            start_link_object = DbLinkConnection.create_link_object(start_node)

        end_link_object = None
        if LinkObject.objects.filter(title=end_node.title).exists():
            end_link_object = LinkObject.objects.get(title=end_node.title)

        if LinkRacerResult.objects.filter(
                start_link=start_link_object,
                end_link=end_link_object).exists():
            result = LinkRacerResult.objects.filter(
                start_link=start_link_object,
                end_link=end_link_object).values_list(
                "link_list_way__link_object__title")
            return [i[0] for i in result]

        # Init start queue
        if LinkConnection.objects.filter(start_link=start_link_object).exists():
            start_url_list = LinkConnection.objects.filter(start_link=start_link_object).values(
                "end_link__title", "end_link__link")
            start_url_dicts = PageSoup.convert_list_to_formated_dicts(start_url_list)
        else:
            start_url_list = start_page.link_list
            start_url_dicts = PageSoup.convert_list_to_formated_dicts(
                start_url_list,
                "end_link__title",
                "end_link__link")

        start_nodes = LinkNode.get_nodes_from_dicts(start_url_dicts, prev_node=start_node)

        # Create connection between start point of parsing list; to every child it has

        list_of_start_links_objects = []

        for node in start_nodes:
            if LinkObject.objects.filter(title=node.title).exists():
                continue
            list_of_start_links_objects.append(
                DbLinkConnection.create_link_object(node)
            )

        for link_object in list_of_start_links_objects:
            if not LinkConnection.objects.filter(
                    start_link=start_link_object,
                    end_link=end_link_object
            ).exists():
                DbLinkConnection.connect_points(start_link_object, link_object, LinkConnection)

        queue = start_nodes
        visited = []
        visited_links = []

        visited.append(start_node)
        page_count = 0
        end_link_title = end_node.title

        for node in queue:
            if node.title == end_link_title:
                return self.trace_backward(node)

        while len(visited) < self.max_redirects:
            current_link_node = queue.pop(0)
            if current_link_node.link in visited_links:
                continue

            print(current_link_node.title)
            print(current_link_node.link)
            sleep(self.requests_per_minute / 60)

            page_count += 1

            if page_count % 10 == 0:
                print(len(queue))
                print(len(visited))

            new_page_soup = PageSoup(current_link_node.link)
            new_links_soup = new_page_soup.link_list
            url_dicts = PageSoup.convert_list_to_formated_dicts(new_links_soup)

            new_nodes = []
            for url_dict in url_dicts:
                link = url_dict.get('link')
                if link == current_link_node.link or link in visited_links:
                    continue
                if any([link == node.link for node in queue]):
                    continue
                new_nodes.append(LinkNode.create_node_from_dict(url_dict, prev_link_node=current_link_node))

            curent_link = LinkObject.objects.get(title=current_link_node.title)

            for node in new_nodes:

                child_exists = LinkObject.objects.filter(title=node.title).exists()
                if not child_exists:
                    child_of_current_link = DbLinkConnection.create_link_object(node)
                else:
                    child_of_current_link = LinkObject.objects.get(title=node.title)

                DbLinkConnection.connect_points(
                    curent_link, child_of_current_link, LinkConnection
                )
                if node.title == end_link_title:
                    trace = self.trace_backward(node)
                    trace_qr = self.save_racer_result(trace)
                    result = [link.link_object.title for link in trace_qr]
                    return result
                queue.append(node)

            visited.append(current_link_node)
            visited_links.append(current_link_node.link)
