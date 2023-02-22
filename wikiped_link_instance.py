class LinkNode:

    def __init__(
            self,
            title: str,
            link: str,
            text: str,
            prev_title: str,
            prev_link: str,
    ) -> None:
        self.title = title
        self.link = link
        self.text = text
        self.prev_title = prev_title
        self.prev_link = prev_link

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"Title - {self.title}, prev - {self.prev_title}"