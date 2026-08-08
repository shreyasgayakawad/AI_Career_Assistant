"""
Supported Job Platforms

Defines the external job platforms supported by
AI Career Assistant.
"""

from enum import StrEnum


class JobPlatform(StrEnum):
    """
    Supported external job platforms.
    """

    LINKEDIN = "LinkedIn"
    NAUKRI = "Naukri"
    INDEED = "Indeed"
    GLASSDOOR = "Glassdoor"
    MONSTER = "Monster"
    SURELYREMOTE = "SurelyRemote"
    FOUNDIT = "Foundit"