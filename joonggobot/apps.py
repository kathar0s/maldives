from django.apps import AppConfig


class JoonggobotConfig(AppConfig):
    name = 'joonggobot'

    def ready(self):
        import joonggobot.signals


