"""Sample domain services."""

from __future__ import annotations

from advanced_alchemy.extensions.litestar import repository, service

from app.db import models as m


class SampleService(service.SQLAlchemyAsyncRepositoryService[m.Sample]):
    """Handles database operations for samples."""

    class Repo(repository.SQLAlchemyAsyncRepository[m.Sample]):
        """Sample SQLAlchemy Repository."""

        model_type = m.Sample

    repository_type = Repo
    match_fields = ["name"]
