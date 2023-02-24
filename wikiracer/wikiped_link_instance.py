from __future__ import annotations


class LinkNode:

    def __init__(
            self,
            title: str,
            link: str,
            text: str,
            prev_link_node: LinkNode = None
    ) -> None:
        self.title = title
        self.link = link
        self.text = text
        self.prev_link_node = prev_link_node

    @classmethod
    def create_node_from_dict(
            cls,
            dict_obj: dict,
            prev_link_node: LinkNode = None
    ) -> LinkNode:
        return cls(**dict_obj, prev_link_node=prev_link_node)

    @staticmethod
    def get_nodes_from_dicts(
            list_of_dicts: list[dict],
            prev_node: LinkNode = None
    ) -> list[LinkNode]:
        return [
            LinkNode.create_node_from_dict(dict_obj, prev_node)
            for dict_obj
            in list_of_dicts
        ]

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        prev = self.prev_link_node.title if self.prev_link_node is not None else None
        return f"<title - {self.title}, prev - {prev} | {hex(id(self))}>"
