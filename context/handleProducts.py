from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectMultipleField, widgets, IntegerRangeField, IntegerField


class MultipleFieldWithCheckboxes(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class handleProductForms(FlaskForm):
    search = StringField('Search')
    formSellers = MultipleFieldWithCheckboxes("Sellers", choices=[])
    reviews = IntegerRangeField("Choices", render_kw={"type": "range", "min": 0, "max": 5}, default=0)
    env_impact = IntegerField('Environmental Impact', default=1000)
    maxPrice = IntegerField('Max Price', default=5000)
    minPrice = IntegerField('Min Price', default=0)
    submit = SubmitField('Submit')
    