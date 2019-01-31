class FileHandleError(Exception):
    pass


class MongoError(Exception):
    pass


class VaultError(Exception):
    pass


class VaultUserNotFound(Exception):
    pass


class VaultUserWordCloudNotAccessible(Exception):
    pass


class ZipFileFound(Exception):
    pass


class InvalidCredentials(Exception):
    pass


class InvalidOtp(Exception):
    pass


class VaultUserWordCloudNotFound(Exception):
    pass


class AnonymizationError(Exception):
    pass


class AnonymizationStatusError(Exception):
    pass


class UserIdError(Exception):
    pass


class UserIdNotFound(Exception):
    pass


class AnonymizeUploadError(Exception):
    pass


class UploadError(Exception):
    pass


class ValidateFileNameError(Exception):
    pass


class SendGridError(Exception):
    pass
