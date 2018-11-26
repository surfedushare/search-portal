import requests

_DEFAULT_API_ENDPOINT = "http://smb.edurep.kennisnet.nl/smdBroker/ws"

_REQUEST_HEADERS = {'content-type': 'application/soap+xml'}
# _REQUEST_HEADERS = {'content-type': 'text/xml'}

_REQUEST_TEMPLATE = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:smd="http://xsd.kennisnet.nl/smd/1.0/"
                  xmlns:hreview="http://xsd.kennisnet.nl/smd/hreview/1.0/">
  <soapenv:Header/>
  <soapenv:Body>
    <smd:insertSMO>
      <smd:smo xmlns:smd="http://xsd.kennisnet.nl/smd/1.0/"
         xmlns:hreview="http://xsd.kennisnet.nl/smd/hreview/1.0/">
          <hreview:hReview>
            <hreview:info>{}</hreview:info>
            <hreview:rating>{}</hreview:rating>
          </hreview:hReview>
          <smd:supplierId>{}</smd:supplierId>
          <smd:userId>{}</smd:userId>
        </smd:smo>
    </smd:insertSMO>
  </soapenv:Body>
</soapenv:Envelope>
"""


class SmbSoapApiClient:

    def __init__(self, api_endpoint=_DEFAULT_API_ENDPOINT):
        self.api_endpoint = api_endpoint

    def send_rating(self, info, rating, supplier_id, user_id):
        body = _REQUEST_TEMPLATE.format(info, rating, supplier_id, user_id)

        response = requests.post(self.api_endpoint, data=body,
                                 headers=_REQUEST_HEADERS)

        if response and response.status_code != requests.codes.ok:
            response.raise_for_status()
