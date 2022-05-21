from email import contentmanager, utils
from django.shortcuts import render
from django import forms
from markdown2 import Markdown
from django.http import HttpResponseRedirect
from django.urls import reverse
from random import choice

from . import util


class NewEntryForm(forms.Form):
    title = forms.CharField(
        label="Entry Name",
        widget=forms.TextInput(attrs={"class": "form-control col-md-8 col-lg-8"}),
    )
    contents = forms.CharField(
        label="Contents",
        widget=forms.Textarea(
            attrs={"class": "form-control col-md-8 col-lg-8", "rows": 10}
        ),
    )
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)


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


def random(request):
    entry = choice(util.list_entries())
    return HttpResponseRedirect(reverse("entry", kwargs={"entry": entry}))


def create(request):
    if request.method == "POST":
        form = NewEntryForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            contents = form.cleaned_data["contents"]
            if (
                util.get_entry(title) is None or form.cleaned_data["edit"] is True
            ):  # Check for existing entry
                util.save_entry(title, contents)
                markdowner = Markdown()
                return HttpResponseRedirect(reverse("entry", kwargs={"entry": title}))
            else:
                return render(
                    request,
                    "encyclopedia/create.html",
                    {"form": form, "existing": True, "entry": title},
                )
        else:
            return render(
                request, "encyclopedia/create.html", {"form": form, "existing": False}
            )
    else:
        return render(
            request,
            "encyclopedia/create.html",
            {"form": NewEntryForm(), "existing": False},
        )


def edit(request, entry):
    page = util.get_entry(entry)
    if page is not None:
        form = NewEntryForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["contents"].initial = page
        form.fields["edit"].initial = True
        return render(
            request,
            "encyclopedia/create.html",
            {"form": form, "edit": True, "entry_name": entry},
        )
    else:
        return render(request, "encyclopedia/error.html", {"entry_name": entry})
