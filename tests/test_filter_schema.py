import pytest
from pydantic import ValidationError

from schemas.filter_agent import (
    DiscardOrgOutput,
    OrganisationOutput,
    FilterOrgBatchOutput,
)


def test_valid_filter_batch_output():

    result = FilterOrgBatchOutput(
        discarded_organizations=[
            DiscardOrgOutput(
                org_name="TestOrg",
                tech_stack_org=["java"],
                missing_skills=["python"],
                reason="No meaningful alignment",
                is_discard=True,
            )
        ],
        organizations=[
            OrganisationOutput(
                org_name="GoodOrg",
                user_entry_id=1,
                status="Pending",
                recent_activity=None,
            )
        ],
    )

    assert isinstance(result, FilterOrgBatchOutput)
    assert len(result.discarded_organizations) == 1
    assert len(result.organizations) == 1


def test_invalid_filter_batch_output():

    with pytest.raises(ValidationError):

        FilterOrgBatchOutput(
            discarded_organizations="not-a-list",
            organizations=[],
        )