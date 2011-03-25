from datetime import datetime

from django import forms

INPUT_FORMATS = ('%m/%d/%Y', '%m/%d/%y',
    '%m-%d-%Y', '%m-%d-%y',
    '%m.%d.%Y', '%m.%d.%y',
)

class MyDateField(forms.DateField):
    
    def __init__(self, *args, **kwargs):
        kwargs['input_formats'] = INPUT_FORMATS
        kwargs['initial'] = datetime.today().strftime('%m/%d/%Y')
        super(MyDateField, self).__init__(*args, **kwargs)
        self.widget.attrs['class'] = 'datepicker'
        self.widget.attrs['size'] = 10
