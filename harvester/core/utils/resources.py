from datagrowth.exceptions import DGResourceDoesNotExist

from core.models import FileResource, TikaResource, YouTubeDLResource


def get_basic_material_resources(url):
    """
    Convenience function to return a file resource and Tika resource based on a URL.

    :param url: URL to search file and Tika resources for
    :return: file_resource, tika_resource
    """
    try:
        file_resource = FileResource(config={"cache_only": True}).get(url)
    except DGResourceDoesNotExist:
        return None, None
    try:
        tika_resource = TikaResource(config={"cache_only": True}).run(file_resource.get_signed_absolute_uri())
    except DGResourceDoesNotExist:
        return file_resource, None
    return file_resource, tika_resource


def get_material_resources(url, language_hint):
    """
    This function returns all Datagrowth Resources available for a URL.
    These resources contain the content of the material while seeds contain the metadata.
    When porting this method I left out the resource that contains the video transcription,
    because that part we probably won't ever port to this harvester.
    Instead this will get replaced with an Amber based resource sometime in the (near) future.
    Another thing to note is that while

    :param url:
    :param language_hint:
    :return:
    """
    # Checking for basic resources
    file_resource, tika_resource = get_basic_material_resources(url)
    if file_resource is None or not file_resource.success or tika_resource is None or not tika_resource.success:
        return file_resource, tika_resource, None, None
    # Early exit for non-video materials to prevent further database lookups
    if not tika_resource.has_video():
        return file_resource, tika_resource, None, None
    # Getting the video download
    try:
        video_resource = YouTubeDLResource(config={"cache_only": True}).run(url)
    except DGResourceDoesNotExist:
        return file_resource, tika_resource, None, None
    _, data = video_resource.content
    file_path = data.get("file_path", None)
    if not video_resource.success or not file_path:
        return file_resource, tika_resource, video_resource, None
    # TODO: get transcriptions with Amber instead of returning None
    return file_resource, tika_resource, video_resource, None
