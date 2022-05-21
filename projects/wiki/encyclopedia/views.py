from django.shortcuts import render
from markdown2 import Markdown

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, entry):
    page = util.get_entry(entry)
    markdowner = Markdown()
    return render(request, "encyclopedia/entry.html", {
        "entry_text": markdowner.convert(page),
        "entry_name": entry
    })
