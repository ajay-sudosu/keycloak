from fastapi import HTTPException
from keycloak.exceptions import KeycloakError, KeycloakPostError


class TokenNotFound(Exception):
    """
    Exception raised when a token is not found or is invalid.

    Attributes:
        status_code (int): The HTTP status code associated with the exception.
        body (str): The description or message associated with the exception.
    """
    def __init__(self, status_code, body):
        """
           Initialize a TokenNotFound exception with the specified status code and body.

           Args:
               status_code (int): The HTTP status code associated with the exception.
               body (str): The description or message associated with the exception.
        """
        self.status_code = status_code
        self.body = body
        super().__init__(self.status_code, self.body)


class Role_requeid(Exception):
    """_summary_
    exception  raise in case role attach or detach  is less than  1
    Args:
        status_code (int): The HTTP status code associated with the exception.
        body (str): The description or message associated with the exception.
    """
    def __init__(self, message):
        """
           Initialize a TokenNotFound exception with the specified status code and body.

           Args:
               status_code (int): The HTTP status code associated with the exception.
               body (str): The description or message associated with the exception.
        """
        self.status_code = 400
        self.body = "bad request"
        self.message = message
        super().__init__(self.status_code, self.body, self.message)


class PydanticException(Exception):
    """
    Exception raised when a Pydantic validations are not proper.

    Attributes:
        status_code (int): The HTTP status code associated with the exception.
        message (str): The description or message associated with the exception.
    """
    def __init__(self, message):
        """
           Initialize a PydanticException exception with the specified status code and body.

           Args:
               message (str): The description or message associated with the exception.
        """
        self.status_code = 400
        self.message = message
        super().__init__(self.status_code, self.message)


class AuthExceptions(KeycloakError):
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(response_code=self.status_code, error_message=self.message)


class DomainException(KeycloakPostError):
    def __init__(self, status_code: int):
        self.message = "Something went wrong"
        self.status_code = status_code
        if self.status_code == 404:
            self.message = "Domain cannot be configured. Server not responding."
        elif self.status_code == 409:
            self.message = "Domain already present. Please try again with another domain name."
        super().__init__(response_code=self.status_code, error_message=self.message)


class NotAuthorized(Exception):
    """
    Exception raised when a token is not found or is invalid.

    Attributes:
        status_code (int): The HTTP status code associated with the exception.
        message (str): The description or message associated with the exception.
    """
    def __init__(self):
        """
           Initialize a TokenNotFound exception with a default status_code and body as error.
        """
        self.status_code = 401
        self.message = "Not authorized to perform this action. Please contact your administrator"
        super().__init__(self.status_code, self.message)


class MetaDataException(TokenNotFound):
    """
    Exception raised when a token is not found or is invalid.

    Attributes:
        status_code (int): The HTTP status code associated with the exception.
        message (str): The description or message associated with the exception.
    """
    def __init__(self, status_code, message):
        """
           Initialize a TokenNotFound exception with the specified status code and body.

           Args:
               status_code (int): The HTTP status code associated with the exception.
               message (str): The description or message associated with the exception.
        """
        self.status_code = status_code
        self.message = message
        super().__init__(self.status_code, self.message)
