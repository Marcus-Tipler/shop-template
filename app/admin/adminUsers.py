from flask_admin.contrib.sqla import ModelView
from wtforms import TextAreaField
from wtforms.widgets import TextArea

class adminUsers(ModelView):
    column_list = ('_id', 'username', 'realname', 'surname', 'email', 'password')
    form_columns = ('username', 'realname', 'surname', 'email', 'password')