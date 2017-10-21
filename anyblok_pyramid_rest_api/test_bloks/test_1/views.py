# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from cornice import Service
from cornice.resource import resource

from marshmallow import Schema, fields

from anyblok_pyramid_rest_api.crud_resource import CrudResource
from anyblok_pyramid_rest_api.validator import (
    body_validator,
    full_validator
)
from anyblok_pyramid_rest_api.schema import FullRequestSchema


class ExampleSchema(Schema):
    """A basic marshmallow schema example
    This one represents the model fields
    """
    id = fields.Int(required=True)
    name = fields.Str(required=True)


class AnotherSchema(FullRequestSchema):
    """This one inherits FullRequestSchema and represents the request
    """
    body = fields.Nested(ExampleSchema(partial=('id',)))
    path = fields.Nested(ExampleSchema(partial=('name',)))


@resource(collection_path='/examples', path='/examples/{id}')
class ExampleResource(CrudResource):
    """CrudResource basic example. No validator, no schema
    """
    ANYBLOK_MODEL = 'Model.Example'


@resource(collection_path='/basevalidator/examples',
          path='/basevalidator/examples/{id}',
          validators=(full_validator,))
class ExampleResourceBaseValidator(CrudResource):
    """CrudResource basic example with base validator
    """
    ANYBLOK_MODEL = 'Model.Example'


# another endpoint through a service with the same model
another_service = Service(name='another_service', path='/anothers/{id}')

# another collection endpoint through a service with the same model
another_collection_service = Service(
    name='another_collection_service',
    path='/anothers')


@another_service.get()
def another_service_get(request):
    """ No validator, no schema
    """
    registry = request.anyblok.registry
    model = registry.get('Model.Example')
    item = model.query().get(request.matchdict['id'])
    return item.to_dict()


@another_service.put(
    validators=(full_validator,),
    schema=AnotherSchema())
def another_service_put(request):
    """ full_validator + AnotherSchema
    """
    registry = request.anyblok.registry
    model = registry.get('Model.Example')
    item = model.query().get(request.validated.get('path').get('id'))
    item.update(**request.validated.get('body'))
    return item.to_dict()


@another_collection_service.post(
    validators=(body_validator,),
    schema=ExampleSchema(partial=('id',)))
def another_service_post(request):
    """ body_validator + schema
    As it is a POST, exclude 'id' from validation with the `partial` arg
    on schema instantiation
    """
    registry = request.anyblok.registry
    model = registry.get('Model.Example')
    item = model.insert(**request.validated)
    return item.to_dict()
