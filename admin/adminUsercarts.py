from flask_admin.contrib.sqla import ModelView
from wtforms import TextAreaField
from wtforms.widgets import TextArea

class adminUsercarts(ModelView):
    column_list = ('_id', 'userID', 'itemIDs', 'amount')
    form_columns = ('userID', 'itemIDs', 'amount')