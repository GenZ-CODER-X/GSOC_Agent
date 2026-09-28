from pydantic import BaseModel, ConfigDict


class DiscardOrgOutput(BaseModel):
    org_name: str
    tech_stack_org: list[str] | None = None
    missing_skills: list[str] | None = None
    reason: str
    is_discard: bool


class OrganisationOutput(BaseModel):
    org_name: str
    user_entry_id: int
    status: str = "Pending"
    recent_activity: str | None = None


class FilterOrgBatchOutput(BaseModel):
    discarded_organizations: list[DiscardOrgOutput]
    organizations: list[OrganisationOutput]