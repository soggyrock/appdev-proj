from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class BlogForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Save')


class CommentForm(FlaskForm):
    author = StringField('Your Name', validators=[DataRequired()])
    content = TextAreaField('Your Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')

