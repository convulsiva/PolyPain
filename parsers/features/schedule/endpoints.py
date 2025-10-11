from furl import furl

BASE_URL = "https://ruz.spbstu.ru"


def get_search_groups_url(external_id: str) -> str:
    return str(furl(BASE_URL).add(path="search/groups").add(args={"q": external_id}))
