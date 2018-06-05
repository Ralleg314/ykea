from django.apps import AppConfig


class YkeaConfig(AppConfig):
    name = 'ykea'
	def ready(self):
        # Makes sure all signal handlers are connected
        from . import handlers  # noqa