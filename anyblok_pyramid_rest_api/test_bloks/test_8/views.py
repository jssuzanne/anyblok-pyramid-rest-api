# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2018 Jean-Sébastien Suzanne <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_pyramid import current_blok
from anyblok_pyramid_rest_api.crud_resource import (
    CrudResource, resource)
from .schema import CustomerSchema, ActionSchema


@resource(
    collection_path='/customers/v8',
    path='/customers/v8/{id}',
    installed_blok=current_blok()
)
class CustomerResourceV8(CrudResource):
    model = 'Model.Customer'
    default_schema = CustomerSchema

    @CrudResource.execute('action1', collection=True, schema=ActionSchema)
    def do_action_1(self):
        return self.body['name']

    @CrudResource.execute('action2', schema=ActionSchema)
    def do_action_2(self):
        return self.body['name']
