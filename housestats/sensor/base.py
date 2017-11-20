import logging

LOG = logging.getLogger(__name__)


class BaseSensor():
    defaults = {}

    def __init__(self, config):
        self.config = self.defaults.copy()
        if config:
            self.config.update(config)
