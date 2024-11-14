# group-16

## Requirements

Make sure you have the following installed:

- [NodeJS](https://nodejs.org) (Recommendation: use [NVM](https://github.com/nvm-sh/nvm) for Linux/Mac or [NVM-Windows](https://github.com/coreybutler/nvm-windows) for Windows to manage multiple versions of NodeJS)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [VS Code](https://code.visualstudio.com/)

If you open this project in VS Code you should get a list of recommended extensions.

## Getting started

### Using Dev Containers

Dev Containers allow you to connect VS Code directly to a Docker container, enabling you to develop inside the container using autocompletion as well as npm and python commands just like on your local machine.

**First Start:**

1. Install the VS Code `Dev Containers` extension by Microsoft, if not already installed.
2. Open the root of this project in VS Code.
3. Open the VS Code command palette: Mac ⇧⌘P, Windows Ctrl+Shift+P.
4. Run `Dev Containers: Rebuild and Reopen in Container`.
5. Choose one of the following options:
   - `Frontend All` - Starts all containers and connects to the frontend container.
   - `Backend All` - Starts all containers and connects to the backend container.
6. Wait for the containers to build and start. The initial load may take some time as it builds all the images (monitor progress by clicking the loading bar in the bottom right).

**Important:** Containers may continue running after closing VS Code. Stop them manually using Docker Desktop or the CLI.

**Shutting Down:**

1. Close VS Code or click the blue button in the bottom left, then select `Close Remote Connection`.
2. Stop the containers using Docker Desktop or the CLI as described in a later section.

**Troubleshooting:**

- If issues arise, try running `Dev Containers: Rebuild Container`.
- If the Flask or Node app isn't running in the terminal, disconnect and restart the container (the npm/flask command runs only when the container starts but continues after disconnection).

### Using Docker Compose in VS Code UI

If you have opened this project in VS Code and installed all recommended extensions, you can start the project by following these steps:

1. Go to the Explorer tab in VS Code.
2. Open the Task Explorer submenu at the bottom.
3. Navigate to `group-16 > vscode`.

Here are the available tasks:

- **Start Dev**: Start the application in development mode.
- **Start Debug**: Start the application in debug mode.
- **Open Frontend**: Open the frontend in your browser.
- **Open Swagger**: Open the backend API documentation in your browser.

Alternatively, you can use the "Tasks: Run Task" command in VS Code to run these tasks. The "Start Dev" task should also appear in the status bar at the bottom of the screen.

### Manually run Docker Compose commands

You can also manually run Docker commands from the root of the project:

```shell
docker compose up --build # Start the application in development mode
docker compose up --build -d # Start the application in development mode in background
docker compose stop # Stop all containers of this project
docker compose down # Stop and remove containers

docker compose -f docker-compose.debug.yml up --build # Start the application in debug mode
```

**Hint:** Debug mode uses a Python Debugger, allowing you to use the "Run and Debug" tab of VS Code. Select "Backend Python Debugger" and click the small green play button in the top left. This will disable hot-reloading.

**Hint:** The default backend port is `4200` and the frontend uses `3000`.

## Test and Deploy

Use the built-in continuous integration in GitLab.

- [ ] [Get started with GitLab CI/CD](https://docs.gitlab.com/ee/ci/quick_start/index.html)
- [ ] [Analyze your code for known vulnerabilities with Static Application Security Testing (SAST)](https://docs.gitlab.com/ee/user/application_security/sast/)
- [ ] [Deploy to Kubernetes, Amazon EC2, or Amazon ECS using Auto Deploy](https://docs.gitlab.com/ee/topics/autodevops/requirements.html)
- [ ] [Use pull-based deployments for improved Kubernetes management](https://docs.gitlab.com/ee/user/clusters/agent/)
- [ ] [Set up protected environments](https://docs.gitlab.com/ee/ci/environments/protected_environments.html)

---

# Editing this README

When you're ready to make this README your own, just edit this file and use the handy template below (or feel free to structure it however you want - this is just a starting point!). Thanks to [makeareadme.com](https://www.makeareadme.com/) for this template.

## Suggestions for a good README

Every project is different, so consider which of these sections apply to yours. The sections used in the template are suggestions for most open source projects. Also keep in mind that while a README can be too long and detailed, too long is better than too short. If you think your README is too long, consider utilizing another form of documentation rather than cutting out information.

## Name

Choose a self-explaining name for your project.

## Description

Let people know what your project can do specifically. Provide context and add a link to any reference visitors might be unfamiliar with. A list of Features or a Background subsection can also be added here. If there are alternatives to your project, this is a good place to list differentiating factors.

## Badges

On some READMEs, you may see small images that convey metadata, such as whether or not all the tests are passing for the project. You can use Shields to add some to your README. Many services also have instructions for adding a badge.

## Visuals

Depending on what you are making, it can be a good idea to include screenshots or even a video (you'll frequently see GIFs rather than actual videos). Tools like ttygif can help, but check out Asciinema for a more sophisticated method.

## Installation

Within a particular ecosystem, there may be a common way of installing things, such as using Yarn, NuGet, or Homebrew. However, consider the possibility that whoever is reading your README is a novice and would like more guidance. Listing specific steps helps remove ambiguity and gets people to using your project as quickly as possible. If it only runs in a specific context like a particular programming language version or operating system or has dependencies that have to be installed manually, also add a Requirements subsection.

## Usage

Use examples liberally, and show the expected output if you can. It's helpful to have inline the smallest example of usage that you can demonstrate, while providing links to more sophisticated examples if they are too long to reasonably include in the README.

## Support

Tell people where they can go to for help. It can be any combination of an issue tracker, a chat room, an email address, etc.

## Roadmap

If you have ideas for releases in the future, it is a good idea to list them in the README.

## Contributing

State if you are open to contributions and what your requirements are for accepting them.

For people who want to make changes to your project, it's helpful to have some documentation on how to get started. Perhaps there is a script that they should run or some environment variables that they need to set. Make these steps explicit. These instructions could also be useful to your future self.

You can also document commands to lint the code or run tests. These steps help to ensure high code quality and reduce the likelihood that the changes inadvertently break something. Having instructions for running tests is especially helpful if it requires external setup, such as starting a Selenium server for testing in a browser.

## Authors and acknowledgment

Show your appreciation to those who have contributed to the project.

## License

For open source projects, say how it is licensed.

## Project status

If you have run out of energy or time for your project, put a note at the top of the README saying that development has slowed down or stopped completely. Someone may choose to fork your project or volunteer to step in as a maintainer or owner, allowing your project to keep going. You can also make an explicit request for maintainers.
