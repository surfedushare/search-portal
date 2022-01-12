import requests
from requests.status_codes import codes

from django.conf import settings


EDUTERM_QUERY_TEMPLATE = "http://api.onderwijsbegrippen.kennisnet.nl/1.0/Query/GetConcept" \
                         "?format=json&apikey={api_key}&concept=<http://purl.edustandaard.nl/concept/{concept}>"
EDUSTANDAARD_TEMPLATE = "{protocol}://purl.edustandaard.nl/begrippenkader/{concept}"
DEEPL_ENDPOINT = "https://api-free.deepl.com/v2/translate"


def translate_with_deepl(dutch_term):
    if not settings.DEEPL_API_KEY:
        return dutch_term

    response = requests.post(DEEPL_ENDPOINT, {
        'auth_key': [settings.DEEPL_API_KEY],
        'text': dutch_term,
        'source_lang': "NL",
        'target_lang': "EN"
    })

    if response.status_code != codes.ok:
        return dutch_term

    json = response.json()
    return json['translations'][0]['text']


def fetch_eduterm_translations(term):
    query_url = EDUTERM_QUERY_TEMPLATE.format(concept=term, api_key=settings.EDUTERM_API_KEY)
    response = requests.get(query_url)

    if response.status_code != codes.ok:
        return

    labels = response.json()["results"]["bindings"]
    if not len(labels):
        return

    default = labels[0]["label"]
    dutch = labels[0].get("label_nl", default)
    english = labels[0].get("label_en", default)

    return dutch['value'], english['value']


def fetch_edustandaard_translations(term):
    query_url = EDUSTANDAARD_TEMPLATE.format(concept=term, protocol="https")
    headers = {'Accept': 'application/json'}
    response = requests.get(query_url, headers=headers)

    if response.status_code != codes.ok:
        return

    json = response.json()
    key = EDUSTANDAARD_TEMPLATE.format(concept=term, protocol="http")

    if not json.get(key, None):
        return

    dutch_value = json[key]['http://www.w3.org/2004/02/skos/core#prefLabel'][0]['value']

    return dutch_value, dutch_value
