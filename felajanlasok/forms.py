from django import forms


class FileUploadForm(forms.Form):
    cel_file = forms.FileField(label='Cél adatok fájl', required=False,
                               help_text='Tabulátorral tagolt CSV fájl a célokról')
    felajanlas_file = forms.FileField(
        label='Felajánlás adatok fájl', required=False,
        help_text='Tabulátorral tagolt CSV fájl a felajánlásokról')
