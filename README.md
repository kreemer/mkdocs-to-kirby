# mkdocs-to-kirby

A MkDocs plugin to export your documentation site for use with [Kirby CMS](https://getkirby.com/).

## Features

- Converts MkDocs pages to Kirby-compatible content files
- Preserves metadata and structure
- Supports custom configuration

## Installation

```bash
pip3 install mkdocs-to-kirby
```

## Usage

Add the plugin to your `mkdocs.yml`:

```yaml
plugins:
    - mkdocs-to-kirby
```

Build your site as usual:

```bash
mkdocs build
```

Exported content will be available in the configured output directory.

## Configuration

Example configuration in `mkdocs.yml`:

```yaml
plugins:
    - mkdocs-to-kirby:
            output_dir: kirby-content
            default_template: "doc"
            # default_language: "en"
```

## Requirements

- Python 3
- MkDocs

## Development

Clone the repository and install dependencies:

```bash
git clone https://github.com/kreemer/mkdocs-to-kirby.git
cd mkdocs-to-kirby
pip3 install -e .
```

## License

MIT

## Contributing

Pull requests and issues are welcome!
