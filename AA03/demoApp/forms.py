from django import forms

Trans = [('foot','Foot'), ('bus','Bus'), ('car','Car')]

class CreateNewList(forms.Form):
    source = forms.CharField(label="Source Address", max_length=200)
    dest = forms.CharField(label="Destination Address", max_length=200)
    method = forms.CharField(label='Method of transport', widget=forms.Select(choices=Trans))
