from django.shortcuts import render
from markdown2 import Markdown

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {"entries": util.list_entries()})


def entry(request, entry):
    page = util.get_entry(entry)
    markdowner = Markdown()
    if page is not None:
        return render(
            request,
            "encyclopedia/entry.html",
            {"entry_text": markdowner.convert(page), "entry_name": entry},
        )
    else:
        return render(request, "encyclopedia/error.html", {"entry_name": entry})


def search(request):
    input = request.GET.get("q", "")
    page = util.get_entry(input)
    if page is not None:
        markdowner = Markdown()
        return render(
            request,
            "encyclopedia/entry.html",
            {"entry_text": markdowner.convert(page), "entry_name": input},
        )
    else:
        search_results = []
        for entry in util.list_entries():
            if input.lower() in entry.lower():
                search_results.append(entry)
        return render(request, "encyclopedia/search.html", {"entries": search_results})
