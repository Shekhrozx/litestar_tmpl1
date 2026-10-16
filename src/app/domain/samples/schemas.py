"""Sample domain schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated
from uuid import UUID

from msgspec import Meta

from app.core.utils.schema import CamelizedBaseStruct


class Sample(CamelizedBaseStruct):
    """Sample response schema."""

    id: UUID
    name: str
    description: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class SampleCreate(CamelizedBaseStruct):
    """Payload for creating a sample."""

    name: Annotated[str, Meta(min_length=10, max_length=255)]
    description: str | None = None


class SampleUpdate(CamelizedBaseStruct):
    """Payload for partially updating a sample."""

    name: str | None = None
    description: str | None = None
