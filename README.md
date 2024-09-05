# Links to Markdown Converter

This project provides a tool that converts URLs into markdown URLs by automatically fetching the title for each link and generating a markdown-formatted list.

## Prerequisites

Ensure you have the following installed:

- Docker
- Docker Compose

## Getting Started

1. Clone the repository and navigate into the project directory.
2. To start the services using Docker, run the following command:

```bash
docker-compose up -d --build
```

This will build the Docker image and start the necessary containers in detached mode.

3. Run any required migrations for the project:

```bash
docker compose exec celery python manage.py migrate django_celery_results
```

This will apply any database migrations necessary for storing the results of the Celery tasks.

## Features

- Enter URLs, and the system will automatically fetch the title and generate markdown-formatted links.
- You can copy the markdown output to the clipboard with one click.

## Usage

1. Start the application using Docker as described above.
2. Open the web interface in your browser (default is `localhost`).
3. Enter your URLs into the input box, one per line.
4. Click the `Convert` button to generate markdown-formatted URLs with their titles fetched automatically.

## Example Output

If you input URLs like this:

```
https://example.com
https://medium.com
```

The output will look like this:

```markdown
- [Example Domain](https://example.com)
- [Medium](https://medium.com)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Feel free to modify the README according to your project's specific requirements!
