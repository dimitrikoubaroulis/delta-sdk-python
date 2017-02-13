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

from abc import ABCMeta, abstractmethod

import six


@six.add_metaclass(ABCMeta)
class ApiClient(object):

    DELTA_URL = 'https://delta.covata.io/v1'        # type: str
    RESOURCE_IDENTITIES = '/identities'             # type: str

    def __init__(self, crypto_service):
        # type: (object) -> ApiClient
        """
        Constructs a new Delta API client with the given configuration.

        :param crypto_service: the CryptoService object
        :type crypto_service: :class:`~covata.delta.crypto.CryptoService`
        """
        self._crypto_service = crypto_service

    @abstractmethod
    def register_identity(self, external_id=None, metadata=None):
        # type: (str or None, dict or None) -> str
        """
        Creates a new identity in Delta with the provided metadata
        and external id.

        :param Optional[str] external_id:
            the external id to associate with the identity

        :param Optional[dict] metadata:
            the metadata to associate with the identity

        :return: the id of the newly created identity

        :rtype: str
        """

    @abstractmethod
    def get_identity(self, requestor_id, identity_id):
        # type: (str, str) -> dict
        """
        Gets the identity matching the given identity id.

        :param str requestor_id: the authenticating identity id
        :param str identity_id: the identity id to retrieve
        :return: the retrieved identity
        :rtype: dict
        """