from datagrowth.resources import ShellResource


class ChromeScreenshotResource(ShellResource):

    CMD_TEMPLATE = [
        "/opt/google/chrome/google-chrome",
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--virtual-time-budget=10000",
        "CMD_FLAGS",
        "{}"
    ]

    FLAGS = {
        "screenshot": "--screenshot="
    }

    @property
    def success(self):
        return self.status == 0 and bool(self.stderr) and "Written to file" in self.stderr
