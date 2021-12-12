from django.http import JsonResponse
from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

import logging
import urllib.request
import re

from .forms import LinksToMarkdownForm

class LinksToMarkdownView(View):
    form_class = LinksToMarkdownForm
    initial = {}
    template_name = 'links_to_markdown/index.html'
    title = "Links to Markdown"
    data = {'title': title}

    def get(self, request, *args, **kwargs):
        print(self.template_name)
        form = self.form_class(initial=self.initial)
        self.data['form'] = form
        return render(request, self.template_name, self.data)

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        titles = []
        if form.is_valid():
            _links = form.cleaned_data['links']
            links = _links.splitlines()
            for link in links:
                with urllib.request.urlopen(link) as f:
                    m = re.search('<title>(.+?)</title>', f.read().decode('utf-8'))
                    if m is not None:
                        titles.append("* [{}]({})".format(m.group(1), link))
            form = self.form_class(initial=self.initial)
            self.initial['markdown'] = '\n'.join(titles)
            self.initial['links'] = _links
        self.data['form'] = form
        return render(request, self.template_name, self.data)
