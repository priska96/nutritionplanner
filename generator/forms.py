from django import forms
from django.core.exceptions import ValidationError
from django.forms import DateInput, NumberInput

from generator.models import Person, MealSet


class PersonForm(forms.ModelForm):
    class Meta:
        model = Person
        exclude = ['plan']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Namen/Pseudonym (nur Buchstaben & Zahlen)'}),
            'height': forms.NumberInput(
                attrs={'placeholder': u'Größe in cm'}),
            'weight': forms.NumberInput(
                attrs={'placeholder': u'Gewicht in kg'}),
            'preferences': forms.TextInput(
                attrs={'placeholder': u'Kommagetrennte Liste von expliziten Lebensmitteln'}),
            'dislikes': forms.TextInput(
                attrs={'placeholder': u'Kommagetrennte Liste von expliziten Lebensmitteln'}),
        }

    def clean(self):
        data = super().clean()
        if 'name' in data and data['name']:
            if not data['name'].isalnum():
                self._errors['name'] = self.error_class([u'Nur Buchstaben und Zahlen sind erlaubt'])
        if 'age' in data and data['age']:
            if data['age'] < 19:
                self._errors['age'] = self.error_class([u'Ein Mindestalter von 19 Jahren ist erforderlich'])
        if 'height' in data and data['height']:
            if not isinstance(data['height'], int):
                self._errors['height'] = self.error_class([u'Gib die Größe in cm an'])
        if 'preferences' in data and data['preferences']:
            words = data['preferences'].split(',')
            words2 = []
            for word in words:
                word = word.strip()
                word = word.casefold()
                word = word.replace('ü', 'ue')
                word = word.replace('ä', 'ae')
                word = word.replace('ö', 'oe')
                words2.append(word)
                word = word[0].upper() + word[1:]
                words2.append(word)
            regex = '|'.join(words2)
            data['preferences'] = regex
        if 'dislikes' in data and data['dislikes']:
            words = data['dislikes'].split(',')
            words2 = []
            for word in words:
                word = word.strip()
                word = word.casefold()
                word = word.replace('ü', 'ue')
                word = word.replace('ä', 'ae')
                word = word.replace('ö', 'oe')
                words2.append(word)
                word = word[0].upper() + word[1:]
                words2.append(word)
            regex = '|'.join(words2)
            data['dislikes'] = regex
        return data


class GeneratorForm(forms.Form):
    hidden_start = forms.DateField(label='Von: ', widget=DateInput(attrs={'type': 'date'}))
    hidden_end = forms.DateField(label='Bis: ', widget=DateInput(attrs={'type': 'date'}))
    person_id = forms.IntegerField(widget=NumberInput(attrs={'type': 'hidden'}))

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['hidden_start'] and cleaned_data['hidden_end']:
            person = Person.objects.get(id=cleaned_data['person_id'])
            meals = MealSet.objects.filter(person=person, date__gte=cleaned_data['hidden_start'], date__lte=cleaned_data['hidden_end'])
            if meals:
                raise forms.ValidationError(u'Für diese Auswahl gibt es bereits Essenspläne.')
        if not cleaned_data['hidden_start'] or not cleaned_data['hidden_end']:
            raise forms.ValidationError(u'Bitte vervollständige deine Auswahl')
        return cleaned_data


