from django.urls import path

from encyclopedia.views import show_entry, index, create_new_entry, edit_page

app_name = "wiki"

urlpatterns = [
    path("", index, name="index"),
    path("<str:title>", show_entry, name="entries"),
    path("new/", create_new_entry, name="new"),
    path("edit/<str:entry>", edit_page, name="edit"),

]

