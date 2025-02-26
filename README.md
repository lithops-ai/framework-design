# Lithops Design Docs

This repository outlines the architecture design of Lithops multi-agent framework.

## Building & Serving Documentation

First install [poetry](https://python-poetry.org/docs/) if you haven't already.

Then, from the project directory, run:

```bash
poetry install --no-root
```

This initializes a project-bound Python environment
with all the tooling required to build the documentation into static webpages
as well as for serving the docs and hot-reloading.

To start the documentation server, run:

```bash
poetry run mkdocs serve
```

By default, the server listens at port 8000.
Open up `http://localhost:8000` in the browser and see the documentation!

## Adding Documentation Files

Add markdown files in the `docs` folder.
After a file is added,
the `nav` section in `mkdocs.yml` must be updated
for the static website to include it.
See the bottom of `mkdocs.yml` for how to do this.
