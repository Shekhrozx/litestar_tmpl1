"""Sample domain controller."""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated
from uuid import UUID

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Parameter

from app.domain.samples import schemas as s
from app.domain.samples.deps import provide_samples_service
from app.domain.samples.guards import requires_sample_access
from app.domain.samples.services import SampleService

if TYPE_CHECKING:
    from collections.abc import Sequence


class SampleController(Controller):
    """Sample routes."""

    path = "/samples"
    tags = ("Samples",)
    guards = [requires_sample_access]
    dependencies = {"samples_service": Provide(provide_samples_service)}
    signature_namespace = {"SampleService": SampleService, "s": s, "UUID": UUID}


    # ----
    @get(
        operation_id="ListSamples",
        path="/",
    )
    async def list_samples(self, samples_service: SampleService) -> Sequence[s.Sample]:
        """List samples."""
        results = await samples_service.list()
        return [samples_service.to_schema(obj, schema_type=s.Sample) for obj in results]

    # ----
    @get(
        operation_id="GetSample",
        path="/{sample_id:uuid}",
    )
    async def get_sample(
        self,
        samples_service: SampleService,
        sample_id: Annotated[UUID, Parameter(title="Sample ID")],
    ) -> s.Sample:
        """Get a sample."""
        obj = await samples_service.get(sample_id)
        return samples_service.to_schema(obj, schema_type=s.Sample)

    # ----
    @post(
        operation_id="CreateSample",
        path="/",
    )
    async def create_sample(self, samples_service: SampleService, data: s.SampleCreate) -> s.Sample:
        """Create a sample."""
        obj = await samples_service.create(data, auto_commit=True)
        return samples_service.to_schema(obj, schema_type=s.Sample)

    # ----
    @patch(
        path="/{sample_id:uuid}",
        operation_id="UpdateSample",
    )
    async def update_sample(
        self,
        samples_service: SampleService,
        data: s.SampleUpdate,
        sample_id: Annotated[UUID, Parameter(title="Sample ID")],
    ) -> s.Sample:
        """Update a sample."""
        obj = await samples_service.update(
            data, item_id=sample_id, auto_commit=True
        )
        return samples_service.to_schema(obj, schema_type=s.Sample)

    # ----
    @delete(
        path="/{sample_id:uuid}",
        operation_id="DeleteSample",
        return_dto=None,
    )
    async def delete_sample(
        self,
        samples_service: SampleService,
        sample_id: Annotated[UUID, Parameter(title="Sample ID")],
    ) -> None:
        """Delete a sample."""
        await samples_service.delete(sample_id, auto_commit=True)
