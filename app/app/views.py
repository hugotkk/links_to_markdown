from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.utils.timezone import now
from uuid import uuid4
import json
import threading
import urllib.request
import re
import ssl
from urllib.parse import urlparse

class LinksToMarkdownView(View):
    template_name = 'links_to_markdown/index.html'
    conversion_status = {}
    conversion_lock = threading.RLock()

    def get(self, request, *args, **kwargs):
        print(self.template_name)
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        if request.headers.get('Content-Type') == 'application/json':
            return self.convert_links(request)
        else:
            return JsonResponse({'error': 'Invalid request'}, status=400)

    def convert_links(self, request):
        try:
            links = json.loads(request.body).get('links')
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        if links:
            task_id = str(uuid4())
            self.initialize_conversion_status(task_id)
            threading.Thread(target=self.process_links, args=(links, task_id)).start()
            return JsonResponse({'task_id': task_id})
        else:
            return JsonResponse({'error': 'No links provided'}, status=400)

    def process_links(self, links, task_id):
        titles = []
        total_links = len(links)
        current_link = 0
        for link in links:
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
            
            current_link += 1
            self.update_conversion_status(task_id, 'processing', '\n'.join(titles), int(current_link / total_links * 100))

        self.update_conversion_status(task_id, 'complete', '\n'.join(titles), 100)

    @classmethod
    def initialize_conversion_status(cls, task_id):
        with cls.conversion_lock:
            cls.conversion_status[task_id] = {
                'status': 'processing',
                'output': '',
                'progress': 0
            }

    @classmethod
    def update_conversion_status(cls, task_id, status, output, progress):
        with cls.conversion_lock:
            if task_id in cls.conversion_status:
                cls.conversion_status[task_id] = {
                    'status': status,
                    'output': output,
                    'progress': progress
                }
                print(f"Updated conversion status for task {task_id}: {cls.conversion_status[task_id]}")
            else:
                print(f"Task {task_id} not found in conversion status")

def get_conversion_status(request):
    task_id = request.GET.get('task_id')
    with LinksToMarkdownView.conversion_lock:
        if task_id in LinksToMarkdownView.conversion_status:
            print(f"Returning conversion status for task {task_id}: {LinksToMarkdownView.conversion_status[task_id]}")
            return JsonResponse(LinksToMarkdownView.conversion_status[task_id])
        else:
            return JsonResponse({'error': 'Conversion not found'}, status=404)
