import requests
import certifi
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

_retry = Retry(total=2, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
_session = requests.Session()
_session.mount("https://", HTTPAdapter(max_retries=_retry))


def get_json(url, params=None, headers=None, timeout=30):
    resp = _session.get(
        url,
        params=params,
        headers=headers,
        timeout=timeout,
        verify=certifi.where(),
    )
    resp.raise_for_status()
    return resp.json()
