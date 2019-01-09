import random
import string

from .. import config
from ..web import base
from pymongo import errors


def generate_master_subject_code(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


class MasterSubjectCodeHandler(base.RequestHandler):
    def post(self):
        payload = self.request.json_body

        if payload['use_patient_id']:
            query = {
                'patient_id': payload['patient_id']
            }
        else:
            query = {
                'first_name': payload['first_name'],
                'last_name': payload['last_name'],
                'date_of_birth': payload['date_of_birth']
            }

        payload.pop('use_patient_id')
        subj_codes = list(config.db.master_subject_codes.find(query))

        if len(subj_codes) > 1:
            self.abort(400, "Found multiple master subject codes")
        elif subj_codes:
            # Update doc with the payload
            try:
                config.db.master_subject_codes.update_one({'_id': subj_codes[0]['_id']}, {'$set': payload})
            except errors.DuplicateKeyError as e:
                self.abort(400, str(e))

            return {'code': subj_codes[0]['_id']}
        else:
            # generate new master subject code
            payload['_id'] = generate_master_subject_code()
            try:
                result = config.db.master_subject_codes.insert_one(payload)
            except errors.DuplicateKeyError as e:
                self.abort(400, str(e))
            else:
                return {'code': result.inserted_id}
