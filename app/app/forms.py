from django import forms

class LinksToMarkdownForm(forms.Form):
    links = forms.CharField(widget=forms.Textarea)
    markdown = forms.CharField(widget=forms.Textarea, required = False)
