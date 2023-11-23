from django import forms
from ads.models import Ad


class AdForm(forms.ModelForm):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)
    class Meta:
        model = Ad
        fields = ('title', 'author','id')


class FileFieldForm(forms.Form):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
