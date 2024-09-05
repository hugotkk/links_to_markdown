from celery import Celery
import urllib.request
import re
import os

app = Celery('tasks', broker=os.environ.get('CELERY_BROKER_URL', 'amqp://guest:guest@localhost:5672//'))
app.conf.update(
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP=True
)

@app.task
def convert_links_to_markdown(links):
    titles = []
    for link in links.splitlines():
        try:
            with urllib.request.urlopen(link) as f:
                m = re.search('<title>(.+?)</title>', f.read().decode('utf-8', errors='ignore'))
                if m is not None:
                    titles.append("* [{}]({})".format(m.group(1), link))
                else:
                    titles.append(f"* [{link}]({link})")
        except (urllib.error.URLError, ValueError):
            titles.append(f"* [Error fetching title for: {link}]({link})")
    return '\n'.join(titles)