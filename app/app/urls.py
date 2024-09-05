from django.urls import path
from . import views

urlpatterns = [
    path('', views.LinksToMarkdownView.as_view(), name='links_to_markdown'),
    path('get_conversion_status', views.get_conversion_status, name='get_conversion_status'),
    path('convert_links', views.LinksToMarkdownView.as_view(), name='convert_links'),
]
