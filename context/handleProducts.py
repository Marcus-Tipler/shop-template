from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectMultipleField, widgets, IntegerRangeField


class MultipleFieldWithCheckboxes(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class handleProductForms(FlaskForm):
    search = StringField('Search')
    choices = MultipleFieldWithCheckboxes("Choices", choices=[])
    # reviews = MultipleFieldWithCheckboxes("Choices", review_types=[0, 1, 2, 3, 4, 5])
    env_impact = IntegerRangeField('Environmental Impact', default=50)
    # price = IntegerRangeField('Price', default=100)
    submit = SubmitField('Submit')
    