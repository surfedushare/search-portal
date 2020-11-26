from sunzip import Sunzip, ZipFilePitfall


class SafeUnzip(Sunzip):
    """
    A Sunzip implementation that respects the interface of zipfile.ZipFile
    """

    def get_zip_file_size(self):
        # Return undecompressd zip file size
        return self.path.size  # path is not actually a path, but a FileField (file is stored on S3)

    def check_is_safe(self):
        """
        Raises ZipFilePitfall if any checks fail and enables Layer 2 protection.
        A method mostly copied from the Sunzip.extract method.
        """

        # Defense Layer 1 - checks perform on the server side.

        # Check if the file format is expected for context.

        if not self.check_is_zipfile():
            raise ZipFilePitfall("File type is not zip format.")

        # Check if it's a nested zip file.
        # NB: confusing naming by Sunzip maintainer
        # The check_is_nested returns False if a zip is nested (because it fails the security check)
        if not self.check_is_nested():
            ZipFilePitfall("Zip file contains nested zip file.")

        # Check if the compression ratio is greater than threshold.
        if self.get_compression_ratio() > self.max_threshold:
            raise ZipFilePitfall("Compression ratio is greater than threshold.")

        # Check if the upload file size exceeds the maximum limit.
        if self.get_zip_file_size() > self.max_filesize_usage:
            raise ZipFilePitfall("File size exceeds the maximum limit.")

        self.log_debug(Sunzip.LOG_INFO, "All rules have checked completely.")
        return True

    def extractall(self, path=None):
        if not self.check_is_safe():
            return

        self.log_debug(Sunzip.LOG_INFO, "Starting to extract all files")
        self.zip_file.extractall(path=path)
        self.log_debug(Sunzip.LOG_INFO, "Extraction complete.")

    def read(self, path):
        if not self.check_is_safe():
            return

        self.log_debug(Sunzip.LOG_INFO, f"Starting to read file: {path}")
        file_descriptor = self.zip_file.read(path)
        self.log_debug(Sunzip.LOG_INFO, "Read complete.")
        return file_descriptor
