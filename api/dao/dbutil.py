import collections
import random
import time

import pymongo

from ..web.errors import APIStorageException


def try_replace_one(db, coll_name, query, update, upsert=False):
    """
    Mongo does not see replace w/ upsert as an atomic action:
    https://jira.mongodb.org/browse/SERVER-14322

    This function will try a replace_one operation, returning the result and if the operation succeeded.
    """

    try:
        result = db[coll_name].replace_one(query, update, upsert=upsert)
    except pymongo.errors.DuplicateKeyError:
        return result, False
    else:
        return result, True


def fault_tolerant_replace_one(db, coll_name, query, update, upsert=False):
    """
    Like try_replace_one, but will retry several times, waiting a random short duration each time.

    Raises an APIStorageException if the retry loop gives up.
    """

    attempts = 0
    while attempts < 10:
        attempts += 1

        result, success = try_replace_one(db, coll_name, query, update, upsert)

        if success:
            return result
        else:
            time.sleep(random.uniform(0.01,0.05))

    raise APIStorageException('Unable to replace object.')


def paginate_find(collection, find_kwargs, pagination):
    """Return paginated `db.coll.find()` results."""
    if pagination:
        if 'filter' in pagination:
            filter_ = find_kwargs.get('filter', {})
            filter_.update(pagination['filter'])
            find_kwargs['filter'] = filter_

        if 'sort' in pagination:
            sort = find_kwargs.get('sort', [])
            if isinstance(sort, basestring):
                sort = [(sort, pymongo.ASCENDING)]
            sort.extend(pagination['sort'])
            find_kwargs['sort'] = sort

        if 'skip' in pagination:
            find_kwargs['skip'] = pagination['skip']

        if 'limit' in pagination:
            find_kwargs['limit'] = pagination['limit']

    return {
        'total': collection.count(find_kwargs.get('filter', {})),
        'results': list(collection.find(**find_kwargs)),
    }


def paginate_pipe(collection, pipeline, pagination):
    """Return paginated `db.coll.aggregate()` results."""
    total_pipeline = pipeline[:]
    if pagination:
        if 'pipe_key' in pagination:
            pipe_key = pagination.pop('pipe_key')
            for key in pagination.get('filter', {}).keys():
                pagination['filter'][pipe_key(key)] = pagination['filter'].pop(key)
            for i, key_order in enumerate(pagination.get('sort', [])):
                key, order = key_order
                pagination['sort'][i] = (pipe_key(key), order)

        if 'filter' in pagination:
            pipeline.append({'$match': pagination['filter']})
            total_pipeline = pipeline[:]

        if 'sort' in pagination:
            pipeline.append({'$sort': collections.OrderedDict(pagination['sort'])})

        if 'skip' in pagination:
            pipeline.append({'$skip': pagination['skip']})

        if 'limit' in pagination:
            pipeline.append({'$limit': pagination['limit']})

    # total_pipeline.append({'$count': 'total'})  # mongo 3.4+
    total_pipeline.append({'$group': {'_id': None, 'total': {'$sum': 1}}})
    total_result = list(collection.aggregate(total_pipeline))
    return {
        'total': total_result[0]['total'] if total_result else 0,
        'results': list(collection.aggregate(pipeline)),
    }
