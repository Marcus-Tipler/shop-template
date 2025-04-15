from flask_admin.contrib.sqla import ModelView
from wtforms import TextAreaField
from wtforms.widgets import TextArea

class adminTechnologies(ModelView):
    column_list = ('_id', 'name', 'price', 'description', 'seller', 'reviews')
    form_columns = ('name', 'price', 'description', 'seller', 'reviews')