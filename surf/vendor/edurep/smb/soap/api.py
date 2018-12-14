"""
This module provides integration with SMB SOAP-service to add/delete reviews
for materials by user.
"""

import requests

_DEFAULT_API_ENDPOINT = "http://smb.edurep.kennisnet.nl/smdBroker/ws"

_REQUEST_HEADERS = {'content-type': 'application/soap+xml'}

_INSERT_TEMPLATE = """
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


_DELETE_TEMPLATE = """
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:smd="http://xsd.kennisnet.nl/smd/1.0/">
 <soapenv:Header/>
 <soapenv:Body>
  <smd:deleteSMO>
   <smd:smo>
    <smd:smoId>{}</smd:smoId>
    <smd:supplierId>{}</smd:supplierId>
   </smd:smo>
  </smd:deleteSMO>
 </soapenv:Body>
</soapenv:Envelope>
"""


class SmbSoapApiClient:
    """
    Class provides integration with SMB SOAP-service
    """
    def __init__(self, api_endpoint=_DEFAULT_API_ENDPOINT):
        self.api_endpoint = api_endpoint

    def send_rating(self, info, rating, supplier_id, user_id):
        """
        Sends rating to EduRep
        :param info: the identifier of reviewed material
        :param rating: rating of material
        :param supplier_id: the identifier of supplier
        :param user_id: the identifier of user
        """
        body = _INSERT_TEMPLATE.format(info, rating, supplier_id, user_id)

        response = requests.post(self.api_endpoint, data=body,
                                 headers=_REQUEST_HEADERS)

        if response and response.status_code != requests.codes.ok:
            response.raise_for_status()

    def remove_review(self, smo_id, supplier_id):
        """
        Removes review of material by user
        :param smo_id: the identifier of SMO record
        :param supplier_id: the identifier of supplier
        """
        body = _DELETE_TEMPLATE.format(smo_id, supplier_id)

        response = requests.post(self.api_endpoint, data=body,
                                 headers=_REQUEST_HEADERS)

        if response and response.status_code != requests.codes.ok:
            response.raise_for_status()
