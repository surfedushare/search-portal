SENSITIVE_VARIABLES = ["details", "user", "response", "groups", "social"]


def strip_surfconext_data(event):
    """
    Used by Sentry to strip sensitive SURF Conext data before sending the event to sentry.io
    """
    # Look at variable information in stacktrace frames for events logging an exception
    for value in event.get("exception", {}).get("values", []):
        sensitive_frames = [
            frame for frame in value["stacktrace"]["frames"]
            if "surfconext" in frame["abs_path"]
        ]
        for sensitive_frame in sensitive_frames:
            for sensitive_variable in SENSITIVE_VARIABLES:
                sensitive_frame["vars"].pop(sensitive_variable, None)
                sensitive_frame["vars"].get("kwargs", {}).pop(sensitive_variable, None)
