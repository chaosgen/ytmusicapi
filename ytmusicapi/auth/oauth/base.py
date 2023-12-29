from typing import Optional, Any, Dict
import time
import json

from .models import BaseTokenDict, DefaultScope, Bearer, RefreshableTokenDict


class Credentials:
    """ Base class representation of YouTubeMusicAPI OAuth Credentials """
    client_id: str
    client_secret: str

    def get_code(self) -> Dict:
        raise NotImplementedError()

    def token_from_code(self, device_code: str) -> RefreshableTokenDict:
        raise NotImplementedError()

    def refresh_token(self, refresh_token: str) -> BaseTokenDict:
        raise NotImplementedError()


class Token:
    """ Base class representation of the YouTubeMusicAPI OAuth token. """
    access_token: str
    refresh_token: str
    expires_in: int
    expires_at: int
    is_expiring: bool

    scope: DefaultScope
    token_type: Bearer

    def __repr__(self) -> str:
        """ Readable version. """
        return f'{self.__class__.__name__}: {self.as_dict()}'

    def as_dict(self) -> RefreshableTokenDict:
        """ Returns dictionary containing underlying token values. """
        return {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'scope': self.scope,
            'expires_at': self.expires_at,
            'expires_in': self.expires_in,
            'token_type': self.token_type
        }

    def as_json(self) -> str:
        # TODO: [PYDANTIC]: add a custom serializer
        return json.dumps(self.as_dict())

    def as_auth(self) -> str:
        """ Returns Authorization header ready str of token_type and access_token. """
        return f'{self.token_type} {self.access_token}'


class OAuthToken(Token):
    """ Wrapper for an OAuth token implementing expiration methods. """

    def __init__(self,
                 access_token: str,
                 refresh_token: str,
                 scope: str,
                 token_type: str,
                 expires_at: Optional[int] = None,
                 expires_in: Optional[int] = None,
                 **_: Optional[Any]):
        """

        :param access_token: active oauth key
        :param refresh_token: access_token's matching oauth refresh string
        :param scope: most likely 'https://www.googleapis.com/auth/youtube'
        :param token_type: commonly 'Bearer'
        :param expires_at: Optional. Unix epoch (seconds) of access token expiration.
        :param expires_in: Optional. Seconds till expiration, assumes/calculates epoch of init.
        :param _: void excess kwargs

        """
        # match baseclass attribute/property format
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._scope = scope

        # set/calculate token expiration using current epoch
        self._expires_at: int = expires_at if expires_at else int(time.time() + expires_in)
        self._token_type = token_type

    def update(self, fresh_access: BaseTokenDict):
        """
        Update access_token and expiration attributes with a BaseTokenDict inplace.
        expires_at attribute set using current epoch, avoid expiration desync
        by passing only recently requested tokens dicts or updating values to compensate.
        """
        self._access_token = fresh_access['access_token']
        self._expires_at = int(time.time() + fresh_access['expires_in'])

    @property
    def access_token(self) -> str:
        return self._access_token

    @property
    def refresh_token(self) -> str:
        return self._refresh_token

    @property
    def token_type(self) -> Bearer:
        return self._token_type

    @property
    def scope(self) -> DefaultScope:
        return self._scope

    @property
    def expires_at(self) -> int:
        return self._expires_at

    @property
    def expires_in(self) -> int:
        return int(self.expires_at - time.time())

    @property
    def is_expiring(self) -> bool:
        return self.expires_in < 60
