from django.shortcuts import render
import markdown2
from encyclopedia.util import list_entries, get_entry, save_entry
from django import forms
from django.http import HttpResponseRedirect


class SearchEntryForm(forms.Form):
    entry = forms.CharField(label="Type entry name you search for:")

#            <input id="new_entry_title" name="title" type="text" placeholder="Write title of new entry">
#            <textarea id="new_entry_content" name="content" placeholder="Text in Markdown"></textarea>


class NewEntryForm(forms.Form):
    title = forms.CharField(label="Title:")
    content = forms.CharField(widget=forms.Textarea, label="Content:")

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
    })


def show_entry(request, title):
    if title.capitalize() in list_entries() or\
            title.upper() in list_entries() or\
            title.lower() in list_entries():
        return render(request, "encyclopedia/entry.html", {
            "entry": markdown2.markdown(get_entry(title)),
            "page_title": title.capitalize(),
            "form": SearchEntryForm(),
        })

    return show_search_results(request, title)


def show_search_results(request, searched_query):
    matched_entries = [entry for entry in list_entries() if searched_query in entry]
    if matched_entries:
        return render(request, "encyclopedia/search_result.html", {
            "results": f"Results for your search '{searched_query}' are:",
            "matched_entries": matched_entries,
            "form": SearchEntryForm(),
        })
    return render(request, "encyclopedia/search_result.html", {
        "results": f'There is no results for particular search: "{searched_query}"',
        "form": SearchEntryForm(),
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
            return save_entry(title, content)

    return render(request, "encyclopedia/create_new_entry.html", {
        "new_entry_form": NewEntryForm(),
})
