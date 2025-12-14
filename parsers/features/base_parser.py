from pathlib import Path

from ..infra.client import Client, configs


class BaseParser:
    def __init__(self, config_box: configs.ConfigBox) -> None:
        self._config_box = config_box
        self._client = Client(self._config_box)

    def set_db_path(self, new_fp: str) -> None:
        if self._client.bootstrapped:
            return
        new_fp = Path(new_fp)
        if not new_fp.suffix:
            new_fp = new_fp.joinpath(self._config_box.cache.name)
        self._config_box.cache.name = str(new_fp)
