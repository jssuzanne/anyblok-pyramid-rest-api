# This file is a part of the AnyBlok / Pyramid / REST api project
#
#    Copyright (C) 2017 Franck Bret <franckbret@gmail.com>
#    Copyright (C) 2017 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
""" A set of methods for crud resource manipulation
# TODO: Add a get_or_create_item method
# TODO: Manage relationship
# TODO: Response objects serialization
"""
from cornice.resource import view as cornice_view
from anyblok.registry import RegistryManagerException
from .querystring import QueryString
from .validator import base_validator


def get_model(registry, modelname):
    try:
        model = registry.get(modelname)
    except RegistryManagerException:
        raise RegistryManagerException(
            "The model %r does not exists" % modelname)

    return model


def get_item(registry, modelname, path={}):
    model = get_model(registry, modelname)
    model_pks = model.get_primary_keys()
    pks = {x: path[x] for x in model_pks}
    item = model.from_primary_keys(**pks)
    return item


def collection_get(request, modelname):
    """Parse request.params, deserialize it and then build an sqla query

    Default behaviour is to search for equal matches where key is a column
    name
    Two special keys are available ('filter[*' and 'order_by[*')

    Filter must be something like 'filter[key][operator]=value' where key
    is mapped to an sql column and operator is one of (eq, ilike, like, lt,
    lte, gt, gte, in, not)

    Order_by must be something like 'order_by[operator]=value' where
    'value' is mapped to an sql column and operator is one of (asc, desc)

    Limit will limit the records quantity
    Offset will apply an offset on records
    """
    model = get_model(request.anyblok.registry, modelname)
    query = model.query()

    headers = request.response.headers
    headers['X-Total-Records'] = str(query.count())

    if request.params:
        # TODO: Implement schema validation to use request.validated
        querystring = QueryString(request, model)
        query = querystring.update_sqlalchemy_query(query)
        # TODO: Advanced pagination with Link Header
        # Link: '<https://api.github.com/user/repos?page=3&per_page=100>;
        # rel="next",
        # <https://api.github.com/user/repos?page=50&per_page=100>;
        # rel="last"'
        headers['X-Count-Records'] = str(query.count())
        # TODO: Etag / timestamp / 304 if no changes
        # TODO: Cache headers
        return query.all().to_dict() if query.count() > 0 else dict()
    else:
        # no querystring, returns all records (maybe we will want to apply
        # some default filters values
        headers['X-Count-Records'] = str(query.count())
        return query.all().to_dict() if query.count() > 0 else dict()


def collection_post(request, modelname):
    """
    """
    model = get_model(request.anyblok.registry, modelname)
    if 'body' in request.validated.keys():
        item = model.insert(**request.validated['body'])
    else:
        item = model.insert(**request.validated)
    return item.to_dict()


def get(request, modelname):
    """
    return a model instance based on path
    """
    item = get_item(
        request.anyblok.registry,
        modelname,
        request.validated.get('path', {})
    )
    if item:
        return item
    else:
        path = ', '.join(
            ['%s=%s' % (x, y)
             for x, y in request.validated.get('path', {}).items()])
        request.errors.add(
            'path', '404 not found',
            'Resource %s with %s does not exist.' % (modelname, path))
        request.errors.status = 404


def put(request, modelname):
    """
    """
    item = get_item(
        request.anyblok.registry,
        modelname,
        request.validated.get('path', {})
    )
    if item:
        item.update(**request.validated['body'])
        return item.to_dict()
    else:
        path = ', '.join(
            ['%s=%s' % (x, y)
             for x, y in request.validated.get('path', {}).items()])
        request.errors.add(
            'path', '404 not found',
            'Resource %s with %s does not exist.' % (modelname, path))
        request.errors.status = 404


def delete(request, modelname):
    """
    """
    item = get_item(
        request.anyblok.registry,
        modelname,
        request.validated.get('path', {})
    )
    if item:
        item.delete()
        request.status = 204
        return {}
    else:
        path = ', '.join(
            ['%s=%s' % (x, y)
             for x, y in request.validated.get('path', {}).items()])
        request.errors.add(
            'path', '404 not found',
            'Resource %s with %s does not exist.' % (modelname, path))
        request.errors.status = 404


class CrudResource(object):
    """ A class that add to cornice resource CRUD abilities on Anyblok models.

    :Example:

    >>> @resource(collection_path='/examples', path='/examples/{id}')
    >>> class ExampleResource(CrudResource):
    >>>     model = 'Model.Example'

    """
    model = None
    QueryString = QueryString
    dschema_get = None

    def __init__(self, request, **kwargs):
        self.request = request
        self.registry = self.request.anyblok.registry

        if not self.model:
            raise ValueError(
                "You must provide a 'model' to use CrudResource class")

    def guess_dschema(self):
        """Guess a deserialization schema instance
        """
        if 'schema' in self.request.current_service.arguments.keys():
            base = self.request.current_service.schema
            if 'body' in base.fields.keys() and base.fields.get('body').nested:
                dschema = base.fields.get('body').nested
                return dschema
            else:
                return base
        else:
            return None

    @cornice_view(validators=(base_validator,))
    def collection_get(self):
        return collection_get(self.request, self.model)

    @cornice_view(validators=(base_validator,))
    def collection_post(self):
        return collection_post(self.request, self.model)

    @cornice_view(validators=(base_validator,))
    def get(self):
        """
        """
        item = get(self.request, self.model)
        if not item:
            return
        if self.dschema_get:
            dschema = self.dschema_get
        else:
            dschema = self.guess_dschema()
        if dschema:
            return dschema.dump(item).data
        else:
            return item.to_dict()

    @cornice_view(validators=(base_validator,))
    def put(self):
        """
        """
        return put(self.request, self.model)

    @cornice_view(validators=(base_validator,))
    def delete(self):
        """
        """
        return delete(self.request, self.model)
