from marshmallow import Schema, fields, validate


class SignUpSchema(Schema):
    username = fields.Str(validate=validate.Length(min=3), required=True)
    password1 = fields.Str(validate=validate.Length(min=3), required=True)
    password2 = fields.Str(validate=validate.Length(min=3), required=True)


class SignInSchema(Schema):
    remember = fields.Str()
    username = fields.Str(validate=validate.Length(min=3), required=True)
    password = fields.Str(validate=validate.Length(min=3), required=True)
