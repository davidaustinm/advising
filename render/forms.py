from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class GPAForm(forms.Form):
    gpa = forms.DecimalField(label="HS GPA",
                             required = False)

    sat = forms.IntegerField(label="SAT Math",
                             required = False)

    act = forms.IntegerField(label="ACT Math",
                             required = False)

    def clean_gpa(self):
        gpa = self.cleaned_data['gpa']
        if gpa == None:
            return gpa
        if gpa < 0:
            raise ValidationError(_('GPA must be positive'))
        if gpa > 5:
            raise ValidationError(_('Is the GPA really greater than 5?'))
        return gpa


    def clean_sat(self):
        sat = self.cleaned_data['sat']
        if sat == None:
            return sat
        if sat < 0:
            raise ValidationError(_('SAT score must be positive'))
        if sat > 800:
            raise ValidationError(_('SAT score must be 800 or lower'))
        return sat


    def clean_act(self):
        act = self.cleaned_data['act']
        if act == None:
            return act
        if act < 0:
            raise ValidationError(_('ACT score must be positive'))
        if act > 36:
            raise ValidationError(_('ACT score must be 36 or lower'))
        return act

            

    
