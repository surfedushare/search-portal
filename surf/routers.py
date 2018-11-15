from rest_framework.routers import DefaultRouter

class CustomRouter(DefaultRouter):

    def __init__(self, *args, **kwargs):
        # add handler to List route for DELETE action
        self.routes[0].mapping["delete"] = 'list_destroy'
        super().__init__(*args, **kwargs)
