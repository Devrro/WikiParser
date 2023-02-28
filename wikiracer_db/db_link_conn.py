from typing import Union, Type

from django.db.transaction import atomic

from wikiracer.wikiped_link_instance import LinkNode
from wikiracer_db.models import LinkObject, LinkConnection, LinkRacerResult, LinkListWay


class DbLinkConnection:
    @staticmethod
    @atomic
    def create_link_object(node: LinkNode) -> LinkObject:
        if not LinkObject.objects.filter(title=node.title).exists():
            link_object = LinkObject.objects.create(
                title=node.title,
                link=node.link,
            )

            return link_object
        return LinkObject.objects.get(title=node.title)

    @staticmethod
    def connect_points(
            from_node: LinkObject,
            to_node: LinkObject,
            db_model: Union[
                Type[LinkConnection],
                Type[LinkRacerResult]]
    ) -> Union[LinkConnection, LinkRacerResult]:
        if not db_model.objects.filter(
                start_link=from_node,
                end_link=to_node
        ).exists():
            return db_model.objects.create(
                start_link=from_node,
                end_link=to_node
            )
        return db_model.objects.get(
            start_link=from_node,
            end_link=to_node)

    @staticmethod
    def save_path_to_db(
            end_points: LinkRacerResult,
            list_index: int,
            link_object: LinkObject
    ) -> LinkListWay:
        return LinkListWay.objects.create(
            end_points=end_points,
            link_index=list_index,
            link_object=link_object
        )
