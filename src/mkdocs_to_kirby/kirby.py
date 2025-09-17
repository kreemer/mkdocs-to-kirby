from logging import Logger
from pathlib import Path
from typing import Union
from mkdocs_to_kirby.config import MkdocsToKirbyPluginConfig

from mkdocs.structure.nav import Navigation
from mkdocs.structure.pages import Page
from mkdocs.structure.nav import Section


class KirbyStructure:
    def __init__(self, url: str, parent: Union[None, "KirbyStructure"] = None) -> None:
        self.url = url
        self.children = list()
        self.page = None  # type: Union[Page, None]
        self.number = None  # type: Union[int, None]
        self.parent = parent

    def add_child(self, child: "KirbyStructure") -> None:
        self.children.append(child)

    def set_page(self, page: Page) -> None:
        self.page = page

    def get_url(self) -> str:
        if self.parent:
            return f"{self.parent.get_url()}/{self.url}".strip("/").strip()
        return self.url.strip("/").strip()

    def assign_number(self, number: int) -> None:
        self.number = number

    def path(self) -> str:
        if self.parent is None and self.url == "":
            return ""

        parent = ""
        if self.parent:
            parent = f"{self.parent.path()}/"

        prefix = ""
        if self.is_draft():
            prefix = "_"
        elif self.number is not None:
            prefix += f"{self.number}_"

        return parent + prefix + self.url

    def get_template(self) -> Union[str, None]:
        if self.page and "template" in self.page.meta:
            return self.page.meta["template"]
        return None

    def is_draft(self) -> bool:
        return False

    def load_kirby_blocks(self) -> dict[str, str]:

        blocks = {}

        blocks["title"] = self.page.title if self.page else "No Title"

        if self.page:
            for key, value in self.page.meta.items():
                blocks[key.lower()] = value

            blocks["text"] = self.page.markdown

        return blocks

    def markdown(self) -> str:

        markdown = ""
        for key, value in self.load_kirby_blocks().items():
            if markdown != "":
                markdown = markdown + f"----\n\n"

            markdown = f"{markdown}{key.title()}: {value}\n\n"

        return markdown

    def __repr__(self) -> str:
        return f"KirbyStructure(url={self.url}, page_exists={ 'true' if self.page else 'false'}, children={self.children})"


class Kirby:
    def __init__(
        self, config: MkdocsToKirbyPluginConfig, nav: Navigation, logger: Logger
    ) -> None:
        self.config = config
        self.navigation = nav
        self.logger = logger
        self.pages = list()
        self.kirby_structure = KirbyStructure("")

    def is_listed(self, page: Page) -> bool:
        """Determine if a page should be listed in the navigation.

        Args:
            page: The page instance.

        Returns:
            True if the page is listed, False otherwise.
        """

        return page in self.navigation.pages

    def register_page(self, page: Page) -> None:
        """Register a page in the Kirby structure.

        Args:
            page: The page instance.
        """

        self.pages.append(page)

        parts = page.url.strip("/").split("/")

        if len(parts) == 1 and parts[0] == "":
            structure = self.kirby_structure
        else:
            structure = self._recursive_register_page(
                self.kirby_structure, parts[0], parts[1:]
            )
        structure.set_page(page)

    def _recursive_register_page(
        self, structure: KirbyStructure, current_part: str, child_parts: list[str]
    ) -> KirbyStructure:
        """Recursively register a page part in the Kirby structure.

        Args:
            structure: The current Kirby structure node.
            current_part: The current part of the page URL being processed.
        """

        found = next(
            (child for child in structure.children if child.url == current_part), None
        )
        if not found:
            found = KirbyStructure(current_part, parent=structure)
            structure.add_child(found)

            self.logger.debug(f"{__name__}: Added new node: {current_part}")

        else:
            self.logger.debug(f"{__name__}: Node already exists: {current_part}")

        if child_parts:
            return self._recursive_register_page(found, child_parts[0], child_parts[1:])

        return found

    def build(self, language: Union[str, None] = None) -> None:
        """Build the Kirby structure."""
        self.logger.debug(
            f"{__name__}: Building Kirby structure for language: {language}"
        )

        self.enumerate_numbering(self.navigation.items, self.kirby_structure)
        self.build_structure(self.kirby_structure, language)

    def enumerate_numbering(self, items: list, structure: KirbyStructure) -> None:
        """Enumerate numbering for the Kirby structure."""
        self.logger.debug(f"{__name__}: Enumerating numbering")

        number = 0

        for item in items:
            if isinstance(item, Page):
                if structure.page == item and structure.page is not None:
                    structure.assign_number(number)
                    self.logger.debug(
                        f"{__name__}: Assigned number {number} to page {structure.page.title}"
                    )
                else:
                    child_structure = next(
                        (child for child in structure.children if child.page == item),
                        None,
                    )
                    if child_structure and isinstance(child_structure, KirbyStructure):
                        child_structure.assign_number(number)
                        self.logger.debug(
                            f"{__name__}: Assigned number {number} to page {child_structure.page}"
                        )
                number += 1
            elif isinstance(item, Section):
                child_structure = next(
                    (
                        child
                        for child in structure.children
                        if child.url == item.title.lower().replace(" ", "_")
                    ),
                    None,
                )
                if child_structure and isinstance(child_structure, KirbyStructure):
                    self.enumerate_numbering(item.children, child_structure)

    def build_structure(
        self, structure: KirbyStructure, language: Union[str, None] = None
    ) -> None:
        """Recursively build the Kirby structure.

        Args:
            structure: The current Kirby structure node.
        """

        template = structure.get_template()
        if not template:
            template = self.config.default_template

        filename = f"{template}.md"
        if language:
            filename = f"{template}.{language}.md"

        full_path = Path(f"{self.config.output_dir}/{structure.path()}")
        full_path.mkdir(parents=True, exist_ok=True)

        with open(f"{full_path}/{filename}", "w", encoding="utf-8") as f:
            f.write(structure.markdown())

        self.logger.debug(
            f"{__name__}: Building structure for {structure.path()}/{filename}"
        )

        for child in structure.children:
            self.build_structure(child)
