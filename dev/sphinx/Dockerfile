# Sphinx documentation Dockerfile for Augment Adam
FROM python:3.11-slim

# Arguments for source and build directories (can be overridden at runtime)
ARG SPHINX_SRC=/workspace/docs
ARG SPHINX_BUILD=/workspace/docs/_build/html
ENV SPHINX_SRC=${SPHINX_SRC}
ENV SPHINX_BUILD=${SPHINX_BUILD}

WORKDIR /workspace

# Install Sphinx and all desired extensions and themes
RUN pip install --no-cache-dir \
    sphinx \
    myst-parser \
    sphinx-autodoc-typehints \
    sphinxcontrib-mermaid \
    sphinx-copybutton \
    sphinx-design \
    sphinx-togglebutton \
    sphinx-tabs \
    furo \
    sphinx-rtd-theme

# Install the Augment Adam package in development mode
# This allows autodoc to import the package
COPY . /workspace
RUN pip install -e .

# Expose port for preview server
EXPOSE 8033

# Entrypoint: build and serve docs (can override with docker run)
CMD sphinx-build -b html $SPHINX_SRC $SPHINX_BUILD && cd $SPHINX_BUILD && python3 -m http.server 8033
