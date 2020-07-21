from surf.apps.users.models import SessionToken


# Fake a logged in user by setting surf_token in the local storage
def login(self, user):
    token, created = SessionToken.objects.get_or_create(user=user)
    self.selenium.get(self.live_server_url)
    self.selenium.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", "surf_token", token.key)


def replace_content(element, text):
    element.click()
    element.clear()
    element.send_keys(text)
