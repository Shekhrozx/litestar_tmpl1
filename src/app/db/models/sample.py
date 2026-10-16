"""Sample database model."""

from __future__ import annotations

from advanced_alchemy.base import UUIDv7AuditBase
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Sample(UUIDv7AuditBase):
    __tablename__ = "sample"
    __table_args__ = {"comment": "Sample records"}

    name: Mapped[str] = mapped_column(String(length=255), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(length=1000), nullable=True, default=None)

    # ORM

    # Properties