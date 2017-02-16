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

import json
import re
from base64 import b64encode
from collections import OrderedDict
from collections import namedtuple
from datetime import datetime

import six.moves.urllib as urllib
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from ..crypto import calculate_sha256hex
from ..utils import LogMixin

__all__ = ["CVTSigner"]

UNDESIRED_HEADERS = ["Connection", "Content-Length"]
SIGNING_ALGORITHM = "CVT1-RSA4096-SHA256"
CVT_DATE_FORMAT = "%Y%m%dT%H%M%SZ"


class SignatureMaterial(namedtuple('SignatureMaterial', [
    'method',
    'uri',
    'query_params',
    'headers_',
    'canonical_headers',
    'signed_headers',
    'hashed_payload',
    'cvt_date'
])):
    def __init__(self, *args, **kwargs):
        super(SignatureMaterial, self).__init__()
        self.__canonical_request = "\n".join([
            self.method,
            self.uri,
            self.query_params,
            self.canonical_headers,
            self.signed_headers,
            self.hashed_payload])

        self.__string_to_sign = "\n".join([
            SIGNING_ALGORITHM,
            self.cvt_date,
            calculate_sha256hex(self.__canonical_request).decode('utf-8')])

    @property
    def canonical_request(self):
        return self.__canonical_request

    @property
    def string_to_sign(self):
        return self.__string_to_sign


class CVTSigner(LogMixin):
    def __init__(self, keystore):
        """
        Creates a Request Signer object to sign a request
        using the CVT1 request signing scheme.

        :param keystore: The KeyStore object
        :type keystore: :class:`~covata.delta.KeyStore`
        """
        self.__keystore = keystore

    def get_signed_headers(self,
                           identity_id,     # type: str
                           method,          # type: str
                           url,             # type: str
                           headers,         # type: Dict[str, str]
                           payload          # type: Optional[bytes]
                           ):
        # type: (...) -> Dict[str, str]
        """
        Gets an updated header dictionary with an authorization header
        signed using the CVT1 request signing scheme.

        :param str identity_id: the authorizing identity id
        :param str method: the HTTP request method
        :param str url: the delta url
        :param headers: the request headers
        :type headers: Dict[str, str]
        :param payload: the request payload
        :type payload: Optional[bytes]
        :return:
            the original headers with additional Cvt-Date, Host, and
            Authorization headers.
        :rtype: Dict[str, str]
        """
        signature_materials = _get_signature_materials(
            method, url, headers, payload)

        self.logger.debug(signature_materials.canonical_request)
        self.logger.debug(signature_materials.string_to_sign)
        signature = self.__sign(signature_materials.string_to_sign, identity_id)
        headers_ = signature_materials.headers_
        headers_["Authorization"] = \
            "{algorithm} Identity={identity_id}, " \
            "SignedHeaders={signed_headers}, Signature={signature}" \
            .format(algorithm=SIGNING_ALGORITHM,
                    identity_id=identity_id,
                    signed_headers=signature_materials.signed_headers,
                    signature=b64encode(signature).decode('utf-8'))
        return headers_

    def __sign(self, string_to_sign, identity_id):
        private_key = self.__keystore.get_private_signing_key(identity_id)
        return private_key.sign(string_to_sign.encode("utf-8"),
                                padding.PSS(mgf=padding.MGF1(hashes.SHA256()),
                                            salt_length=32),
                                hashes.SHA256())


def _get_signature_materials(method, url, headers, payload):
    # type: (str, str, Dict[str, str], Optional[bytes]) -> SignatureMaterial
    url_parsed = urllib.parse.urlparse(url)
    cvt_date = datetime.utcnow().strftime(CVT_DATE_FORMAT)
    headers_ = dict(headers)
    headers_["Cvt-Date"] = cvt_date
    headers_['Host'] = url_parsed.hostname

    # /master/identities/a123?key=an+arbitrary+value&key2=x
    uri = __encode_uri("/".join(url_parsed.path.split("/")[2:]))
    query = url_parsed.query.replace("+", "%20")

    sorted_header = OrderedDict(sorted(
        (k.lower(), re.sub("\s+", ' ', v).strip())
        for k, v in headers_.items()
        if k not in UNDESIRED_HEADERS))

    canonical_headers = "\n ".join(
        "{}:{}".format(k, v) for (k, v) in sorted_header.items())

    signed_headers = ";".join(sorted_header.keys())
    hashed_payload = __get_hashed_payload(payload)

    return SignatureMaterial(method=method,
                             uri=uri,
                             headers_=headers_,
                             query_params=query,
                             canonical_headers=canonical_headers,
                             signed_headers=signed_headers,
                             hashed_payload=hashed_payload,
                             cvt_date=cvt_date)


def __get_hashed_payload(payload):
    # type: (bytes) -> str
    sorted_payload = "{}" if payload is None else json.dumps(
        json.loads(payload.decode('utf-8')),
        separators=(',', ':'),
        sort_keys=True)
    return calculate_sha256hex(sorted_payload).decode('utf-8')


def __encode_uri(resource_path):
    # type: (str) -> str
    if resource_path is not "/":
        uri_parsed = re.sub("^/+|/+$", "", resource_path)
        quoted_uri = urllib.parse.quote(uri_parsed).replace("%7E", "~")
        return "/{}/".format(quoted_uri)
    else:
        return resource_path
