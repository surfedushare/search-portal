from langid.langid import LanguageIdentifier, model


detector = LanguageIdentifier.from_modelstring(model, norm_probs=False)
detector.set_languages(["en", "nl"])


def get_language_from_snippet(snippet, default=None):
    if not snippet:
        return default
    language = detector.classify(snippet[:1000])  # somewhat arbitrary, but 1000 should cover it I think
    return language[0] if language else default


def get_kaldi_model_from_snippet(snippet, default_language=None):
    language = get_language_from_snippet(snippet, default=default_language)
    if language == "nl":
        return "pol_harvester.KaldiNLResource"
    elif language == "en":
        return "pol_harvester.KaldiAspireResource"
