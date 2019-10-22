from flask_wtf import FlaskForm
from wtforms import FieldList, FormField, StringField, SelectField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional, NumberRange
from flask_wtf.file import FileField

class addNewItemForm(FlaskForm):
    class Meta:
        csrf = True
    pName = StringField('Product Name',
                        validators=[DataRequired(), Length(min=0, max=50)])
    pPrice= IntegerField('Product Price ',
                        validators=[DataRequired()])
    pWeight= IntegerField('Product Weight(grams) ',
                        validators=[DataRequired()])
    # photo1 = FileField('Add Photo')
    # photo2 = FileField(validators=[FileRequired()])
    # photo3 = FileField(validators=[FileRequired()])
    # photo4 = FileField(validators=[FileRequired()])
    # photo5 = FileField(validators=[FileRequired()])
    # photo6 = FileField(validators=[FileRequired()])
    submit = SubmitField('Add Product')
    

