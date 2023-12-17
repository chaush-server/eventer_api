from enum import Enum


class ProviderEnum(Enum):
    SYSTEM = 'SYSTEM'
    ESIA = 'ESIA'
    GOOGLE = 'GOOGLE'


class ValidateStatusEnum(Enum):
    REQUIRED = 'REQUIRED'
    OPTIONAL = 'OPTIONAL'
    NOT_REQUIRED = 'NOT_REQUIRED'


class StatusEnum(Enum):
    ACTIVE = 'ACTIVE'
    APPROVED = 'APPROVED'
    POSPOND = 'POSPOND'
    REJECTED = 'REJECTED'


class TicketTypeEnum(Enum):
    NUMERIC = 'NUMERIC'
    FREE = 'FREE'
