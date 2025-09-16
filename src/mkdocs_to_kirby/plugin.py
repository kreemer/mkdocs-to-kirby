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
        logger.info("MkDocs to Kirby plugin initialized!")
        self.kirby_metadata_list = {}
        self.kirby_structure = {}

        """Clean output directory before building."""

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
        self, nav: Navigation, config: MkDocsConfig, files: Files
    ) -> Union[Navigation, None]:
        """Called after the site navigation is created and can be used to modify the
        site navigation.

        Args:
            nav: The site navigation instance.
            config: Global configuration object.
            files: All files that are part of the build.

        Returns:
            The modified or new navigation instance.
        """

        language = None
        i18n = config.plugins.get("i18n")
        if i18n:
            language = i18n.current_language

        self.prepare_tree(nav.items, language=language)

        return nav

    def prepare_tree(self, items, current_directory="", language=None):
        i = 0
        for item in items:
            if isinstance(item, Section):
                title = str(item.title).replace(" ", "-").lower()
            elif isinstance(item, Page):
                title = str(os.path.basename(item.file.src_path)).replace(".md", "")

            if title != "index":
                if current_directory != "":
                    directory = f"{current_directory}/{i}_{title}"
                else:
                    directory = f"{i}_{title}"
            else:
                directory = current_directory

            if isinstance(item, Section):
                self.prepare_tree(item.children, directory, language)
            elif isinstance(item, Page):
                path = f"{directory}/doc.{language}.md"
                self.kirby_metadata_list[item.file.abs_src_path] = KirbyContent(path)
                self.kirby_structure[os.path.dirname(str(item.file.abs_src_path))] = (
                    current_directory
                )
            i += 1

    def on_page_markdown(
        self, markdown: str, page: Page, config: MkDocsConfig, files: Files
    ) -> Union[str, None]:
        """Called after the page's markdown is loaded and can be used to modify the
        markdown source text.

        Args:
            markdown: The markdown source text of the page.
            page: The page instance.
            config: Global configuration object.
            files: All files that are part of the build.

        Returns:
            The modified or new markdown source text of the page.
        """

        kt = markdown
        if page.file.abs_src_path in self.kirby_metadata_list:
            kirby_metadata = self.kirby_metadata_list[page.file.abs_src_path]
            kirby_blocks = {}
            if "title" in page.meta:
                kirby_blocks["Title"] = page.meta["title"]
            elif str(page.title).lower() != "index":
                kirby_blocks["Title"] = page.title
            elif page.parent:
                kirby_blocks["Title"] = page.parent.title

            for meta_key in page.meta:
                if meta_key != "title":
                    kirby_blocks[meta_key] = page.meta[meta_key]

            # Fix assets
            assets = {}
            for asset in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", markdown):
                parsed_asset = urlparse(asset[1])
                if parsed_asset.scheme or parsed_asset.netloc:
                    continue

                abs_src_path = str(page.file.abs_src_path)
                path = os.path.abspath(
                    os.path.dirname(abs_src_path) + "/" + parsed_asset.path
                )
                name = os.path.basename(parsed_asset.path)

                if not os.path.isfile(path):
                    logger.warning(
                        f"Asset '{path}' not found for page '{page.file.src_path}'"
                    )
                    continue

                if path not in assets:
                    assets[name] = path
                kt = kt.replace(asset[1], f"{name}")

            # Fix links
            kt = re.sub(
                r"(?<!!)\[([^\]]+)\]\(([^)]+)\)",
                lambda m: f"[{m.group(1)}]({self.fix_link(m.group(2))})",
                kt,
            )

            kirby_blocks["Text"] = "\n\n" + kt
            kirby_content = ""
            for block_key in kirby_blocks:
                block_value = kirby_blocks[block_key]
                if kirby_content != "":
                    kirby_content = (
                        kirby_content
                        + f"----\n\n{block_key.title()}: {block_value}\n\n"
                    )
                else:
                    kirby_content = f"{block_key.title()}: {block_value}\n\n"

            self.write_kirby_file(kirby_metadata.path, kirby_content, assets)
        else:
            logger.info(f"Page '{page.file.src_path}' not listed")
        return markdown

    def write_kirby_file(self, path: str, content: str, assets: Dict[str, str]) -> None:
        full_path = Path(f"{self.config.output_dir}/{path}")
        full_path.parent.mkdir(parents=True, exist_ok=True)

        for asset_name in assets:
            asset_src_path = assets[asset_name]
            shutil.copy2(asset_src_path, full_path.parent / asset_name)

        with open(f"{self.config.output_dir}/{path}", "w", encoding="utf-8") as f:
            f.write(content)

    def fix_link(self, link: str) -> str:

        parsed_url = urlparse(link)

        if parsed_url.scheme or parsed_url.netloc:
            return link

        parsed_path = parsed_url.path

        if parsed_path.endswith("index.md"):
            parsed_path = parsed_path[:-8]
        if parsed_path.endswith(".md"):
            parsed_path = parsed_path[:-3]
        if parsed_path.startswith("./"):
            parsed_path = parsed_path[2:]
        if parsed_path.startswith("/"):
            parsed_path = parsed_path[1:]
        # Because Kirby pages lives in subfolders
        # we have to append ../ to the beginning of the path
        parsed_path = f"../{parsed_path}"

        return parsed_path
