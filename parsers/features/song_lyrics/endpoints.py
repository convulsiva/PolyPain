from furl import furl

BASE_URL = "https://vse-pesni.com/"


def get_search_texts_url(search_str: str) -> str:
    return str(furl(BASE_URL).add(args={"s": search_str, "submit": "Поиск"}))


def get_text_url(slug: str) -> str:
    return str(furl(BASE_URL).add(path=f"/song/{slug}"))
