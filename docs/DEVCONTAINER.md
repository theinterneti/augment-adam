# VS Code Devcontainer

The Augment Adam project uses a VS Code devcontainer to provide a consistent development environment for all contributors.

## What is a Devcontainer?

A devcontainer is a Docker container that is specifically configured for development. It includes all the tools and dependencies needed for development, and it can be used with Visual Studio Code to provide a consistent development environment.

## Benefits of Using the Devcontainer

- **Consistent Environment**: All developers work in the same environment, regardless of their local setup.
- **Pre-installed Dependencies**: All required dependencies are pre-installed in the container.
- **Isolated Environment**: The development environment is isolated from your local system.
- **Easy Setup**: Setting up the development environment is as simple as opening the project in VS Code.

## Prerequisites

To use the devcontainer, you need:

- [Visual Studio Code](https://code.visualstudio.com/)
- [Docker](https://www.docker.com/products/docker-desktop)
- [Remote - Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) for VS Code

## Getting Started

1. Clone the repository:
   ```bash
   git clone https://github.com/theinterneti/augment-adam.git
   cd augment-adam
   ```

2. Open the project in VS Code:
   ```bash
   code .
   ```

3. When prompted, click "Reopen in Container" or use the command palette (F1) and select "Remote-Containers: Reopen in Container".

4. VS Code will build the devcontainer and open the project inside it. This may take a few minutes the first time.

5. Once inside the devcontainer, all dependencies are already installed and the environment is ready to use.

## Devcontainer Configuration

The devcontainer configuration is defined in the `.devcontainer` directory:

- `devcontainer.json`: Defines the container configuration, including the Docker image, extensions to install, and other settings.
- `Dockerfile`: Defines the Docker image to use for the devcontainer.

## Working with the Devcontainer

### Terminal

You can open a terminal in the devcontainer by clicking on the "Terminal" menu in VS Code and selecting "New Terminal". The terminal will be running inside the container.

### Extensions

The devcontainer comes with several VS Code extensions pre-installed, including:

- Python
- Pylance
- Docker
- Git
- GitHub Pull Requests
- EditorConfig

### Debugging

You can debug your code inside the devcontainer using VS Code's debugging features. The devcontainer includes the necessary configuration for debugging Python code.

### File Changes

Any changes you make to files in the project will be reflected in your local file system, as the project directory is mounted into the container.

## Troubleshooting

### Container Build Fails

If the container build fails, try:

1. Checking the Docker logs for more information
2. Rebuilding the container using the command palette: "Remote-Containers: Rebuild Container"
3. Ensuring Docker is running and has enough resources allocated

### Port Conflicts

If you encounter port conflicts, you may need to change the ports used in the devcontainer configuration or stop other services using those ports.

### Performance Issues

If you experience performance issues, consider:

1. Increasing the resources allocated to Docker
2. Using a volume mount for better performance on macOS and Windows
3. Excluding large directories from the container using the `workspaceMount` setting

## Additional Resources

- [VS Code Remote Development](https://code.visualstudio.com/docs/remote/remote-overview)
- [Developing inside a Container](https://code.visualstudio.com/docs/remote/containers)
- [Advanced Container Configuration](https://code.visualstudio.com/docs/remote/containers-advanced)
