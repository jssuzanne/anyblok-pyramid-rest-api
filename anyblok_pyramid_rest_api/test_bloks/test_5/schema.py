# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sébastien Suzanne <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok_marshmallow.schema import ModelSchema
from anyblok_marshmallow.fields import Nested


class CitySchema(ModelSchema):

    class Meta:
        model = 'Model.City'


class TagSchema(ModelSchema):

    class Meta:
        model = 'Model.Tag'


class AddressSchema(ModelSchema):

    # follow the relationship Many2One and One2One
    city = Nested(CitySchema)

    class Meta:
        model = 'Model.Address'


class CustomerSchema(ModelSchema):
    """Schema for 'Model.Customer'
    """

    # follow the relationship One2Many and Many2Many
    # - the many=True is required because it is *2Many
    # - exclude is used to forbid the recurse loop
    addresses = Nested(AddressSchema, many=True, exclude=('customer', ))
    tags = Nested(TagSchema, many=True)

    class Meta:
        model = 'Model.Customer'
