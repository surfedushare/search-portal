from core.models import HarvestHttpResource


class EdurepJsonSearchResource(HarvestHttpResource):

    URI_TEMPLATE = "https://wszoeken.edurep.kennisnet.nl/jsonsearch?" \
                    "query=%2A%20AND%20about.repository%20exact%20" \
                    + "{}" + \
                    "%20AND%20%28schema%3AeducationalLevel.schema%3AtermCode%20exact%20" \
                    "bbbd99c6-cf49-4980-baed-12388f8dcff4%20OR%20schema%3AeducationalLevel.schema%3A" \
                    "termCode%20exact%20be140797-803f-4b9e-81cc-5572c711e09c%29"
