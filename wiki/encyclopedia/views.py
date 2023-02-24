from django.shortcuts import render
import markdown2
from .util import list_entries, get_entry, save_entry
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from random import choice


class SearchEntryForm(forms.Form):
    entry = forms.CharField(label="Type entry name you search for:")

#            <input id="new_entry_title" name="title" type="text" placeholder="Write title of new entry">
#            <textarea id="new_entry_content" name="content" placeholder="Text in Markdown"></textarea>


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title:")
    content = forms.CharField(widget=forms.Textarea, label="Content:")


class EditEntryForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea)


# return list of entries that has name with "part of string" in entry - fo through all entries - not case-sensitive
def list_entries_that_search_text_presented_in_entry(search_text):
    return [entry for entry in list_entries() if search_text.casefold() in entry.casefold()]


# entry already exists - is in list of all entries
def title_already_in_entries(title):
    return title.casefold() in [entry.casefold() for entry in list_entries()]


def index(request):
    # Check if method is POST
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = SearchEntryForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the task from the 'cleaned' version of form data
            entry = form.cleaned_data["entry"]

            # return url with entry
            return HttpResponseRedirect(f'/wiki/{entry}')

    return render(request, f"encyclopedia/index.html", {
        "entries": list_entries(),
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })


def show_entry(request, title):
    if title_already_in_entries(title):
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown2.markdown(get_entry(title)),
            "page_title": title,
            "form": SearchEntryForm(),
            "random_page": f'/wiki/{choice(list_entries())}'
        })

    return show_search_results(request, title)


def show_search_results(request, searched_query):
    matched_entries = list_entries_that_search_text_presented_in_entry(searched_query)
    if matched_entries:
        return render(request, "encyclopedia/search_result.html", {
            "results": f"Results for your search '{searched_query}' are:",
            "matched_entries": matched_entries,
            "form": SearchEntryForm(),
            "random_page": f'/wiki/{choice(list_entries())}'
        })
    return render(request, "encyclopedia/search_result.html", {
        "results": f'There is no results for particular search: "{searched_query}"',
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })


def create_new_entry(request):
    # Check if method is POST
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = NewEntryForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the task from the 'cleaned' version of form data
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]

            if title_already_in_entries(title):
                return render(request, f"encyclopedia/index.html", {
                    "error": "Error: Entry already exist",
                    "form": SearchEntryForm(),
                    "random_page": f'/wiki/{choice(list_entries())}'
                })

            save_entry(title, content)
            return show_entry(request, title)
            # return HttpResponseRedirect(reverse(f"wiki:index"))

    return render(request, "encyclopedia/create_new_entry.html", {
        "new_entry_form": NewEntryForm(),
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })


def edit_page(request, entry):
    # Check if method is POST
    content = get_entry(entry)
    # Check if method is POST
    if request.method == "POST":
        print("was post request")
        # Take in the data the user submitted and save it as form
        form = EditEntryForm(request.POST)
        print(form)
        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the task from the 'cleaned' version of form data
            payload_content = form.cleaned_data["content"]

            save_entry(entry, payload_content)
            return HttpResponseRedirect(reverse("wiki:entries"))
#            return render(request, "encyclopedia/entry.html", {
#                "entry": markdown2.markdown(get_entry(entry)),
#                "page_title": entry,
#                "form": SearchEntryForm(),
 #               "random_page": f'/wiki/{choice(list_entries())}'
 #           })
    a = EditEntryForm(initial={'content': content})
    return render(request, "encyclopedia/edit.html", {
        "edit_entry_form": a,
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}',
        "entry": entry,
        "content": content,
    })
