from django import forms

from .models import Application


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = [
            "rector_application",
            "passport",
            "diploma",
            "m_diploma",
            "degree_diploma",
            "qualification_cert",
            "scientific_works",
            "language_cert",
            "resume",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        file_input_classes = "block w-full text-sm text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-gray-200 rounded-lg bg-gray-50 p-1"
        for field in self.fields.values():
            field.widget.attrs.update({"class": file_input_classes})
