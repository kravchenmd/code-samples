from wtforms_alchemy import ModelForm

from src.models import Tag, Note


class TagForm(ModelForm):
    class Meta:
        model = Tag
        fields = ['name']


class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ['name', 'description']
