import logging
import os
import re
from typing import Dict, Literal, Union
from pathlib import Path
import shutil
from urllib.parse import urlparse, urlunparse

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import BasePlugin
from mkdocs.structure.files import Files
from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Section
from mkdocs.utils.templates import TemplateContext

from mkdocs_to_kirby.config import MkdocsToKirbyPluginConfig
from mkdocs_to_kirby.kirby import Kirby

logger = logging.getLogger("mkdocs.plugins")


class KirbyContent:
    def __init__(self, path: str) -> None:
        self.path = path

    def __repr__(self) -> str:
        return f"KirbyContent(path={self.path})"


class MkdocsToKirbyPlugin(BasePlugin[MkdocsToKirbyPluginConfig]):
    def on_startup(
        self, command: Literal["build", "gh-deploy", "serve"], dirty: bool, **kwargs
    ) -> None:
        """Called once when the plugin is loaded.

        Args:
            command: The command being run, one of "build", "gh-deploy" or "serve".
            dirty: Whether to only build files that have changed since the last build.
            **kwargs: Additional keyword arguments.
        """
        logger.debug(
            f"{__name__}: Initialize plugin with command={command}, dirty={dirty}"
        )
        self.kirby = None

        logger.debug(f"{__name__}: Clean output directory before building")
        output_dir = Path(self.config.output_dir)
        if output_dir.exists() and output_dir.is_dir():
            for item in output_dir.iterdir():
                if item.is_dir():

                    shutil.rmtree(item)
                else:
                    item.unlink()
        else:
            output_dir.mkdir(parents=True, exist_ok=True)

    def on_nav(
        self, nav: Navigation, *, config: MkDocsConfig, files: Files
    ) -> Navigation:
        """Process the navigation structure.

        Args:
            nav: The navigation object.
            config: Global configuration object.
            files: Global files collection.

        Returns:
            The processed navigation object.
        """

        logger.debug(f"{__name__}: Processing navigation structure")

        language = self.config.default_language
        if "i18n" in config.plugins:
            i18n_plugin = config.plugins["i18n"]
            if hasattr(i18n_plugin, "current_language"):
                language = i18n_plugin.current_language  # type: ignore

        self.kirby = Kirby(self.config, nav, logger, language)

        return nav

    def on_page_markdown(
        self, markdown: str, /, *, page: Page, config: MkDocsConfig, files: Files
    ) -> str | None:
        logger.debug(
            f"{__name__}: Processing loaded page markdown: {page.file.src_path}"
        )

        if not self.kirby:
            logger.warning(f"{__name__}: Kirby instance is not initialized.")
            return markdown

        is_default_language_build = True
        if "i18n" in config.plugins:
            i18n_plugin = config.plugins["i18n"]
            if hasattr(i18n_plugin, "is_default_language_build"):
                is_default_language_build = i18n_plugin.is_default_language_build  # type: ignore

        self.kirby.register_page(page, is_default_language_build)

    def on_post_build(self, *, config: MkDocsConfig) -> None:
        """Called after the site has been built.

        Args:
            config: Global configuration object.
        """

        logger.debug(f"{__name__}: Post build processing")
        if not self.kirby:
            logger.warning(f"{__name__}: Kirby instance is not initialized.")
            return

        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        language = self.config.default_language
        if "i18n" in config.plugins:
            i18n_plugin = config.plugins["i18n"]
            if hasattr(i18n_plugin, "current_language"):
                language = i18n_plugin.current_language  # type: ignore

        self.kirby.build(language)

        logger.info(
            f"{__name__}: Generated {len(self.kirby.pages)} pages in {self.config.output_dir}"
        )
