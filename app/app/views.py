from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.core.cache import cache
import json
from .tasks import convert_links_to_markdown
from celery.result import AsyncResult

class LinksToMarkdownView(View):
    template_name = 'links_to_markdown/index.html'

    def get(self, request, *args, **kwargs):
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
            task = convert_links_to_markdown.delay(links)
            cache.set(f'links_{task.id}', links, timeout=3600)  # Store links in cache for 1 hour
            return JsonResponse({'task_id': task.id})
        else:
            return JsonResponse({'error': 'No links provided'}, status=400)

def get_conversion_status(request):
    task_id = request.GET.get('task_id')
    task = AsyncResult(task_id)
    links = cache.get(f'links_{task_id}', [])
    
    if task.state == 'PENDING':
        response = {
            'status': 'pending',
            'output': 'Conversion not started...',
            'progress': 0,
            'links': links
        }
    elif task.state == 'PROGRESS':
        response = {
            'status': 'processing',
            'output': task.info.get('status', ''),
            'progress': int((task.info.get('current', 0) / task.info.get('total', 1)) * 100),
            'links': links
        }
    elif task.state == 'SUCCESS':
        result = task.result
        response = {
            'status': 'complete',
            'output': result.get('output', ''),
            'progress': 100,
            'links': links
        }
    else:
        response = {
            'status': 'error',
            'output': str(task.info),
            'progress': 0,
            'links': links
        }
    return JsonResponse(response)
