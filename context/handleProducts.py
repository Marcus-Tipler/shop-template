from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectMultipleField, widgets, IntegerRangeField


class MultipleFieldWithCheckboxes(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class handleProductForms(FlaskForm):
    search = StringField('Search')
    formSellers = MultipleFieldWithCheckboxes("Sellers", choices=[])
    reviews = IntegerRangeField("Choices", render_kw={"type": "range", "min": 0, "max": 5}, default=0)
    env_impact = IntegerRangeField('Environmental Impact', default=100)
    maxPrice = IntegerRangeField('Price', default=100)
    minPrice = IntegerRangeField('Price', default=0)
    submit = SubmitField('Submit')
    