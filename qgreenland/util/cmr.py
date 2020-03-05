import csv
import datetime
import pprint
from collections import namedtuple

import requests

from qgreenland.constants import REQUEST_TIMEOUT

CMR_CLIENT_ID_HEADER = {'Client-Id': 'nsidc-qgreenland'}
CMR_BASE_URL = 'https://cmr.earthdata.nasa.gov'
CMR_GRANULES_URL = f'{CMR_BASE_URL}/search/granules.csv'

CMR_GRANULES_SCROLL_URL = (
    CMR_GRANULES_URL +
    '?provider=NSIDC_ECS&scroll=true&page_size=2000&'
    'sort_key[]=%2Bstart_date&online_only=true'
)

Granule = namedtuple('Granule', ['urls', 'start_time'])


def _clean_granules_csv(granules):
    """Filter out blank lines."""
    return [g for g in granules if g]


def _csv_granules_to_dicts(resp_text):
    granules_csv = _clean_granules_csv(resp_text.split('\n'))

    return list(csv.DictReader(granules_csv))


def get_cmr_granule(*, granule_ur):
    """Queries CMR for a granule by Granule UR, returns a `Granule`."""

    def _normalize_granule(granule):
        """Create a standardized object from a row extracted from the CMR CSV.

        NOTE: The CSV module uses the first row of the response to get the
        labels. If CMR changes their labels, we will have problems. Same would
        be true if the field order changed, and we have no control over that.
        NOTE: The "Online Access URLs" field can have >1 entry for
        some collections. Currently none of them are implemented.
        """
        url = granule['Online Access URLs']
        start_time = datetime.datetime.strptime(
            granule['Start Time'],
            '%Y-%m-%dT%H:%M:%SZ'
        )

        if not url:
            msg = 'CMR response contains a granule without Online Access URLs: {}'
            raise RuntimeError(msg.format(granule))

        return Granule(urls=tuple(url.split(',')), start_time=start_time)

    url = (f'{CMR_GRANULES_SCROLL_URL}'
           f'&granule_ur[]={granule_ur}')
    response = requests.get(url,
                            headers=CMR_CLIENT_ID_HEADER,
                            timeout=REQUEST_TIMEOUT)

    if not response.ok:
        raise RuntimeError('Error from CMR: {}'.format(response.text))

    granules = _csv_granules_to_dicts(response.text)

    if len(granules) > 1:
        raise RuntimeError('Expecting only one granule')

    return _normalize_granule(granules[0])


def search_cmr_granules(*, short_name, version):
    """Only supports one page of results, limited to 2000 granules."""

    def _version_query_string(version):
        max_pad_length = 3
        versions_needed = (max_pad_length - len(str(version))) + 1
        versions = [version.zfill(n+1) for n in range(versions_needed)]
        return ''.join([f'&version={v}' for v in versions])

    url = (f'{CMR_GRANULES_SCROLL_URL}'
           f'&short_name={short_name}'
           f'{_version_query_string(version)}')

    response = requests.get(url,
                            headers=CMR_CLIENT_ID_HEADER,
                            timeout=REQUEST_TIMEOUT)

    if not response.ok:
        raise RuntimeError('Error from CMR: {}'.format(response.text))

    return _csv_granules_to_dicts(response.text)


def pretty_search_cmr_granules(**kwargs):
    try:
        pprint.pprint(search_cmr_granules(**kwargs))
    except BrokenPipeError:
        pass
