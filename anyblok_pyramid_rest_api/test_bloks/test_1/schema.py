# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from marshmallow import Schema, fields

from anyblok_pyramid_rest_api.schema import (
    FullRequestSchema,
)


class ExampleSchema(Schema):
    """A basic marshmallow schema example
    This one represents the model.Example fields
    """
    id = fields.Int(required=True)
    name = fields.Str(required=True)


class AnotherSchema(FullRequestSchema):
    """This one inherits FullRequestSchema and represents the request model.Example
    """
    body = fields.Nested(ExampleSchema(partial=('id',)))
    path = fields.Nested(ExampleSchema(only=('id',)))


class ThingSchema(Schema):
    """Schema for the Thing model
    """
    uuid = fields.UUID(required=True)
    name = fields.Str(required=True)
    secret = fields.Str(required=True, load_only=True)
    example_id = fields.Int(required=True)
    example = fields.Nested(ExampleSchema())
    create_date = fields.DateTime(dump_only=True)
    update_date = fields.DateTime(dump_only=True)


class ThingRequestSchema(FullRequestSchema):
    """This one inherits FullRequestSchema and represents the request for Thing
    model
    """
    body = fields.Nested(ThingSchema(
        partial=('uuid', 'name', 'secret', 'example_id')))
    path = fields.Nested(ThingSchema(only=('uuid',)))
