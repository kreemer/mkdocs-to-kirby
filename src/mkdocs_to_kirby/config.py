from mkdocs.config import config_options
from mkdocs.config.base import Config


class MkdocsToKirbyPluginConfig(Config):
    output_dir = config_options.Type(str, default="kirby-content")
    default_template = config_options.Type(str, default="doc")
    default_language = config_options.Optional(config_options.Type(str))
