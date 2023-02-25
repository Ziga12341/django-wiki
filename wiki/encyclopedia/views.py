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


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title:")
    content = forms.CharField(widget=forms.Textarea, label="Content:")


class EditEntryForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, label="", help_text="")


# return list of entries that has name with "part of string" in entry - fo through all entries - not case-sensitive
def list_entries_that_search_text_presented_in_entry(search_text):
    return [entry for entry in list_entries() if search_text.casefold() in entry.casefold()]


# entry already exists - is in list of all entries
def title_of_entry_already_in_entries(title):
    return title.casefold() in [entry.casefold() for entry in list_entries()]


def index(request):
    return render(request, f"encyclopedia/index.html", {
        "entries": list_entries(),
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })


def search(request):
    # Check if method is POST
    if request.method == "POST":

        # Take in the data the user submitted and save it as form
        form = SearchEntryForm(request.POST)

        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the task from the 'cleaned' version of form data
            searched_query = form.cleaned_data["entry"]

            if title_of_entry_already_in_entries(searched_query):
                # return url with entry
                return HttpResponseRedirect(f'/wiki/{searched_query}')

            return show_search_results(request, searched_query)

    return render(request, f"encyclopedia/search.html", {
        "search": "Search on left side of the page",
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })

def show_entry(request, title):
    if title_of_entry_already_in_entries(title):
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown2.markdown(get_entry(title)),
            "page_title":    title,
            "form": SearchEntryForm(),
            "random_page": f'/wiki/{choice(list_entries())}'
        })
    return HttpResponseRedirect(reverse('wiki:error', args=(f"Requested entry '{title}' not exists",)))


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

            if title_of_entry_already_in_entries(title):
                return HttpResponseRedirect(reverse('wiki:error', args=("Entry already exist",)))

            # when saved it add additional new lines...
            save_entry(title, content)
            # reverse redirection how to pass arguments docs to url:
            # https://docs.djangoproject.com/en/4.0/topics/http/urls/#reverse
            return HttpResponseRedirect(reverse('wiki:entries', args=(title,)))

    return render(request, "encyclopedia/create_new_entry.html", {
        "new_entry_form": NewEntryForm(),
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })


def edit_page(request, entry):
    # get entry content from get entry function
    content = get_entry(entry)

    # Check if method is POST
    if request.method == "POST":
        # Take in the data the user submitted and save it as form
        form = EditEntryForm(request.POST)
        # Check if form data is valid (server-side)
        if form.is_valid():

            # Isolate the task from the 'cleaned' version of form data
            payload_content = form.cleaned_data["content"]

            # save with blank line after newline
            save_entry(entry, payload_content)

            # works just fine
            # return HttpResponseRedirect(f'/wiki/{entry}')

            # reverse redirection how to pass arguments docs to url:
            # https://docs.djangoproject.com/en/4.0/topics/http/urls/#reverse
            return HttpResponseRedirect(reverse('wiki:entries', args=(entry,)))

    return render(request, "encyclopedia/edit.html", {
        # initial value of textarea
        "edit_entry_form": EditEntryForm(initial={'content': content}, auto_id=False),
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}',
        "entry": entry,
    })


def show_error(request, error_message):
    return render(request, f"encyclopedia/error.html", {
        "error": error_message,
        "form": SearchEntryForm(),
        "random_page": f'/wiki/{choice(list_entries())}'
    })