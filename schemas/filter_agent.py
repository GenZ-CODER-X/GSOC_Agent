from pydantic import BaseModel, ConfigDict


class DiscardOrgOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    org_name: str
    tech_stack_org: list[str] | None
    missing_skills: list[str] | None 
    reason: str


class OrganisationOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    org_name: str


class FilterOrgBatchOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    discarded_organizations: list[DiscardOrgOutput]
    organizations: list[OrganisationOutput]