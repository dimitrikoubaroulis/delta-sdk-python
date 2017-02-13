#   Copyright 2017 Covata Limited or its affiliates
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

from __future__ import absolute_import

import requests

from covata.delta.util import LogMixin
from covata.delta.api import ApiClient


class RequestsApiClient(ApiClient, LogMixin):
    def register_identity(self, external_id=None, metadata=None):
        crypto = self._crypto_service
        signing_private_key = crypto.generate_key()
        crypto_private_key = crypto.generate_key()

        signing_public_key = signing_private_key.public_key()
        crypto_public_key = crypto_private_key.public_key()

        body = dict(signingPublicKey=crypto.serialized(signing_public_key),
                    cryptoPublicKey=crypto.serialized(crypto_public_key),
                    externalId=external_id,
                    metadata=metadata)

        response = requests.post(
            url=self.DELTA_URL + self.RESOURCE_IDENTITIES,
            json=dict((k, v) for k, v in body.items() if v is not None))

        identity_id = response.json()['identityId']

        crypto.save(signing_private_key, identity_id + ".signing.pem")
        crypto.save(crypto_private_key, identity_id + ".crypto.pem")

        return identity_id

    def get_identity(self, requestor_id, identity_id):
        return requests.get(
            url="{base_url}{resource}/{identity_id}".format(
                base_url=self.DELTA_URL,
                resource=self.RESOURCE_IDENTITIES,
                identity_id=identity_id),
            auth=self._crypto_service.signer(requestor_id)).json()