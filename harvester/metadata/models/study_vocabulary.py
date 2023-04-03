from datagrowth.resources import HttpResource


class StudyVocabularyResource(HttpResource):

    URI_TEMPLATE = "https://vocabulaires.edurep.nl/type/vak/{}"
