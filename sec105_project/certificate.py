"""Define the Certificate class which represents a x.509v3 certificate.

default: a default value for the attribute (used when creating a new instance of the class and the attribute is not provided)
alias: an alternate name for the attribute
title: a human-readable title for the attribute
description: a description of the attribute and its purpose
regex : the pattern of the input string
The class also uses the root_validator decorator to validate the datetime format of the not_before and not_after attributes.
"""
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List

from pydantic import BaseModel
from pydantic import Field
from pydantic import root_validator


class Certificate(BaseModel):
    """
    A class representing a x.509v3 certificate.

    :param version: The version number of the certificate.
    :type version: int
    :param serial_number: The unique serial number of the certificate.
    :type serial_number: str
    :param signature_algorithm: The algorithm used to sign the certificate.
    :type signature_algorithm: str
    :param issuer: Information about the entity that issued the certificate.
    :type issuer: Dict[str, str]
    :param subject: Information about the subject of the certificate.
    :type subject: Dict[str, str]
    :param not_before: The date from which the certificate is valid.
    :type not_before: datetime
    :param not_after: The date until which the certificate is valid.
    :type not_after: datetime
    :param public_key: Information about the public key of the certificate.
    :type public_key: Dict[str, str]
    :param extensions: Additional information about the certificate.
    :type extensions: List[Dict[str, str]]
    """

    version: int = Field(
        default=...,
        alias="version",
        title="Version",
        description="The version number of the certificate",
    )

    serial_number: str = Field(
        default=...,
        alias="serialNumber",
        title="Serial Number",
        description="The unique serial number of the certificate",
        regex="^[A-Za-z0-9]{16}$",
    )

    signature_algorithm: str = Field(
        default=...,
        alias="signatureAlgorithm",
        title="Signature Algorithm",
        description="The algorithm used to sign the certificate",
    )

    issuer: Dict[str, str] = Field(
        default=...,
        alias="issuer",
        title="Issuer",
        description="Information about the entity that issued the certificate",
    )

    subject: Dict[str, str] = Field(
        default=...,
        alias="subject",
        title="Subject",
        description="Information about the subject of the certificate",
    )

    not_before: datetime = Field(
        default=...,
        alias="validity/notBefore",
        title="Valid from",
        description="The date from which the certificate is valid",
        validator=lambda v: datetime.strptime(v, "%Y-%m-%d %H:%M:%S"),
    )

    not_after: datetime = Field(
        default=...,
        alias="validity/notAfter",
        title="Valid until",
        description="The date until which the certificate is valid",
        validator=lambda v: datetime.strptime(v, "%Y-%m-%d %H:%M:%S"),
    )

    public_key: Dict[str, str] = Field(
        default=...,
        alias="subjectPublicKeyInfo",
        title="Public key",
        description="Information about the public key of the certificate",
    )

    extensions: List[Dict[str, str]] = Field(
        default=...,
        alias="extensions",
        title="Extensions",
        description="Additional information about the certificate",
    )

    @classmethod
    @root_validator(pre=True)
    def validate_datetime(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check the datetime format of not_before and not_after fields.

        This method uses the datetime.strptime() method to parse the not_before and not_after fields
        and raises a ValueError if the input does not match the expected format "YYYY-MM-DD HH:MM:SS".

        :param cls: The class object
        :type cls: type
        :param values: The dictionary containing the input values
        :type values: Dict[str, Any]
        :return: The dictionary containing the parsed datetime values
        :rtype: Dict[str, Any]
        """
        not_before = values.get("not_before")
        not_after = values.get("not_after")
        if not_before:
            try:
                values["not_before"] = datetime.strptime(
                    not_before, "%Y-%m-%d %H:%M:%S"
                )
            except ValueError as exc:
                raise ValueError(
                    "Invalid date format for not_before. Expected format: YYYY-MM-DD HH:MM:SS"
                ) from exc
        if not_after:
            try:
                values["not_after"] = datetime.strptime(not_after, "%Y-%m-%d %H:%M:%S")
            except ValueError as exc:
                raise ValueError(
                    "Invalid date format for not_after. Expected format: YYYY-MM-DD HH:MM:SS"
                ) from exc
        return values
