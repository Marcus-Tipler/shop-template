from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectMultipleField, widgets


class MultipleFieldWithCheckboxes(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class handleProductForms(FlaskForm):
    search = StringField('Search')
    choices = MultipleFieldWithCheckboxes("Choices", choices=[])
    submit = SubmitField('Submit')
    