import init_django_orm  # noqa
from wikiracer.wikiracing import WikiRacer


def main():
    wiki_racer_instance = WikiRacer()
    result = wiki_racer_instance.find_path("Дружба", "Рим")
    print(result)

if __name__ == "__main__":
    main()
