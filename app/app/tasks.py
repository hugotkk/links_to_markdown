from celery import shared_task
import urllib.request
import re
import ssl
from urllib.parse import urlparse

@shared_task(bind=True)
def convert_links_to_markdown(self, links):
    total_links = len(links)
    titles = []

    for i, link in enumerate(links):
        try:
            parsed_url = urlparse(link)
            if not parsed_url.scheme:
                link = 'https://' + link

            context = ssl._create_unverified_context()
            req = urllib.request.Request(
                link,
                data=None,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            )
            with urllib.request.urlopen(req, context=context, timeout=10) as f:
                content = f.read().decode('utf-8', errors='ignore')
                m = re.search('<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
                if m:
                    title = m.group(1).strip()
                    titles.append(f"* [{title}]({link})")
                else:
                    domain = parsed_url.netloc or parsed_url.path.split('/')[0]
                    titles.append(f"* [{domain}]({link})")
        except Exception as e:
            print(f"Error processing {link}: {str(e)}")
            domain = urlparse(link).netloc or link.split('/')[0]
            titles.append(f"* [{domain}]({link})")
        
        # Update progress
        self.update_state(state='PROGRESS',
                          meta={'current': i + 1, 'total': total_links,
                                'status': f'Processing link {i + 1} of {total_links}'})

    result = '\n'.join(titles)
    # Update state to SUCCESS when task is complete
    self.update_state(state='SUCCESS',
                      meta={'current': total_links, 'total': total_links,
                            'status': 'Conversion complete'})
    return {'status': 'Conversion complete', 'output': result}