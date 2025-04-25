#!/bin/bash
# Script to install VS Code extensions in the devcontainer

set -e

echo "Installing VS Code extensions..."

# Python development
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-python.black-formatter
code --install-extension ms-python.flake8
code --install-extension ms-python.isort
code --install-extension matangover.mypy

# AI assistance
code --install-extension Augment.vscode-augment
code --install-extension github.copilot
code --install-extension github.copilot-chat
code --install-extension github.copilot-labs
code --install-extension google.geminicodeassist

# Jupyter and data science
code --install-extension ms-toolsai.jupyter
code --install-extension ms-toolsai.jupyter-keymap
code --install-extension ms-toolsai.jupyter-renderers
code --install-extension ms-toolsai.vscode-jupyter-cell-tags
code --install-extension ms-toolsai.vscode-jupyter-slideshow

# Docker and containers
code --install-extension ms-azuretools.vscode-docker
code --install-extension ms-vscode-remote.remote-containers
code --install-extension ms-vscode-remote.remote-wsl

# Database tools
code --install-extension cweijan.vscode-database-client2
code --install-extension neo4j-extensions.neo4j-for-vscode
code --install-extension redis-labs.redisinsight-vscode

# Git and collaboration
code --install-extension eamodio.gitlens
code --install-extension mhutchie.git-graph
code --install-extension github.vscode-pull-request-github

# Web development
code --install-extension esbenp.prettier-vscode
code --install-extension dbaeumer.vscode-eslint
code --install-extension bradlc.vscode-tailwindcss

# Markdown and documentation
code --install-extension yzhang.markdown-all-in-one
code --install-extension bierner.markdown-preview-github-styles
code --install-extension davidanson.vscode-markdownlint

# Productivity and UI
code --install-extension usernamehw.errorlens
code --install-extension gruntfuggly.todo-tree
code --install-extension streetsidesoftware.code-spell-checker
code --install-extension visualstudioexptteam.vscodeintellicode
code --install-extension wayou.vscode-todo-highlight
code --install-extension oderwat.indent-rainbow

# Testing
code --install-extension littlefoxteam.vscode-python-test-adapter
code --install-extension ryanluker.vscode-coverage-gutters

# REST API development
code --install-extension humao.rest-client
code --install-extension 42crunch.vscode-openapi

echo "VS Code extensions installation completed!"
