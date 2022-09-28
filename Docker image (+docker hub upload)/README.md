# Docker image

## Preparing the environment for Docker

- Virtual env is created using `poetry`
- Files `.toml`, `.lock` are generated
- File `requirements.txt` for Docker is generated as well

![img.png](images/project.png)

## Building the Docker image

- Docker image is built
- Application starts in the container:

![img.png](images/run_docker.png)

- It's possible to start the app via CLI of the container:

![img.png](images/docker_cli.png)


- Finally, the image was successfully uploaded to DockerHub:

![img.png](images/docker_hub.png)
