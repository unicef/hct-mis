from django import forms
from django.templatetags.static import static


class HTMLEditor(forms.Textarea):
    template_name = "changelog/widgets/editor.html"

    def __init__(self, *args, **kwargs):
        theme = kwargs.pop("theme", "snow")
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "formatter-editor"
        self.attrs["theme"] = theme

    class Media:
        css = {
            "all": (
                static("admin/changelog/easymde/easymde.min.css"),
            )
        }
        js = (
            static("admin/changelog/easymde/easymde.min.js"),
        )
