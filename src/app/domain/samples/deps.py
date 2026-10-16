"""Sample domain dependencies."""

from __future__ import annotations

from uuid import UUID

from app.core.settings import constants
from app.core.utils.deps import create_service_dependencies, create_service_provider
from app.domain.samples.services import SampleService

provide_samples_service = create_service_provider(
    SampleService,
    load = [
        # selectinload(m.User.roles).options(joinedload(m.UserRole.role, innerjoin=True)),
        # selectinload(m.User.oauth_accounts),
        # selectinload(m.User.teams).options(
        #     joinedload(m.TeamMember.team, innerjoin=True).options(load_only(m.Team.name)),
        # ),
    ],
    error_messages={
        "duplicate_key": "Sample with this name already exists.",
        "integrity": "Sample operation failed.",
    },
)


inference_service_filter_dependency = create_service_dependencies(
    SampleService,
    key="samples_service",
    load = [
        # selectinload(m.InferenceProc.user).options(
        #     load_only(m.User.id, m.User.email)
        # ),
    ],
    filters={
        "id_filter": UUID,
        "created_at": True,
        "updated_at": True,
        "sort_field": "created_at",
        "sort_order": "desc",
        "search": "data_path,project_id",
        "pagination_type": "limit_offset",
        "pagination_size": constants.DEFAULT_PAGINATION_SIZE,
    },
    error_messages={
        "duplicate_key": "This Sample already exists.",
        "not_found": "This Sample does not exist.",
        "integrity": "Sample integrity error.",
        "other": "An error occurred while processing the Sample.",
    }
)


__all__ = (
    "inference_service_filter_dependency",
    "provide_samples_service",
)