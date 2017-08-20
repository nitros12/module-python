
class ApiError(Exception):
    """Base API error class."""

    def __init__(self, name: str, description: str, id: str, status: int, **extra):
        """
        :param name: The name of the error.
        :param desc: The description of the error.
        :param status: HTTP status code returned.
        :param extra: extra params given in the error response.
        """
        self.name = name
        self.desc = description
        self.id = id
        self.status = status
        self.extra = extra

    def __str__(self):
        return f"API Error id({self.id}) {self.name} {self.desc}. (http code: {self.status}) Extra attrs: {self.extra}"


class DataValidationError(ApiError):
    """Something doesn't match (Maybe you sent a string instead of a number or something)."""


class InvalidOption(ApiError):
    """An option that was provided returned invalid results."""


class RateLimit(ApiError):
    """YOU JUST GOT RATELIMITED BOI."""


class NotEnoughDetail(ApiError):
    """Not all of the required details were submitted with your request."""


class NoQuery(ApiError):
    """You didn't provide a query with your GET request."""


class NoAuth(ApiError):
    """No auth header was sent."""


class LogsDisabled(ApiError):
    """Viewing the logs is disabled."""


class NotAnError(ApiError):
    """This is an error because the error you requested doesn't exist. oh... my... god."""


class LolMemes(ApiError):
    """You just got BAMBOOZLED."""


class FeatureDisabled(ApiError):
    """This feature isn's currently supported."""


class BotCreationFailed(ApiError):
    """Something went wrong and we couldn't create your bot."""


class Nightmare(ApiError):
    """Just an error."""


class DataInputFailed(ApiError):
    """The import of your data failed."""


class NoHeaders(ApiError):
    """You didn't send us any headers with your request?!?!?!?!."""


class UnknownError(ApiError):
    """Something has gone wrong (Nevs UK server probably died). Devs have been alerted."""


class WrongAuthHeaders(ApiError):
    """You have provided an invalid type of authentication for this endpoint."""


class WrongDomain(ApiError):
    """You've connected with the wrong domain name or IP address."""


class NoEventType(ApiError):
    """That event type doesn't exist."""


class MiscUserError(ApiError):
    """The user might not exist or something has gone HORRIBLY WRONG."""


class NoData(ApiError):
    """There's no data for this bot & eventType."""


class AuthFailed(ApiError):
    """Invalid token."""


class LengthMismatch(ApiError):
    """The length of data provided didn't match what we were expecting."""


class WrongToken(ApiError):
    """That token doesn't exist."""


class UserNotNotified(ApiError):
    """Your account isn't verified."""


class BotNonExistant(ApiError):
    """That bot doesn't exist."""
