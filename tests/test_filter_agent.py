from unittest.mock import Mock, patch

import agents.filter_org as filter_org_module
from schemas.filter_agent import (
    DiscardOrgOutput,
    OrganisationOutput,
    FilterOrgBatchOutput,
)


def test_filter_org_processes_batch_once():

    fake_org_info = {
        "FOSSASIA": {
            "name": "FOSSASIA",
            "technologies": ["python", "javascript"],
            "topics": ["open source"],
        },
        "Metaflow": {
            "name": "Metaflow",
            "technologies": ["python", "machine learning"],
            "topics": ["data science"],
        },
    }

    # This is what we pretend Gemini returned.
    fake_llm_result = FilterOrgBatchOutput(
        discarded_organizations=[
            DiscardOrgOutput(
                org_name="FOSSASIA",
                tech_stack_org=["python", "javascript"],
                missing_skills=["Backend"],
                reason="No meaningful backend alignment.",
                is_discard=True,
            )
        ],
        organizations=[
            OrganisationOutput(
                org_name="Metaflow",
                user_entry_id=6,
                status="Pending",
                recent_activity=None,
            )
        ],
    )

    # Mock structured LLM
    fake_structured_model = Mock()
    fake_structured_model.invoke.return_value = fake_llm_result

    # Mock Gemini model
    fake_model = Mock()
    fake_model.with_structured_output.return_value = fake_structured_model

    with patch(
        "agents.filter_org.gsoc_org_page.get_org_details_gsoc_page",
        return_value=fake_org_info,
    ), patch(
        "agents.filter_org.ChatGoogleGenerativeAI",
        return_value=fake_model,
    ):

        result = filter_org_module.filter_org()

    # ------------------------------------------------
    # 1. Verify returned object is the correct schema
    # ------------------------------------------------

    assert isinstance(result, FilterOrgBatchOutput)

    # ------------------------------------------------
    # 2. Verify both lists exist
    # ------------------------------------------------

    assert isinstance(result.discarded_organizations, list)
    assert isinstance(result.organizations, list)

    # ------------------------------------------------
    # 3. Verify contents of discarded organization
    # ------------------------------------------------

    discarded = result.discarded_organizations[0]

    assert isinstance(discarded, DiscardOrgOutput)
    assert discarded.org_name == "FOSSASIA"
    assert discarded.tech_stack_org == ["python", "javascript"]
    assert discarded.missing_skills == ["Backend"]
    assert discarded.is_discard is True

    # ------------------------------------------------
    # 4. Verify contents of kept organization
    # ------------------------------------------------

    kept = result.organizations[0]

    assert isinstance(kept, OrganisationOutput)
    assert kept.org_name == "Metaflow"
    assert kept.user_entry_id == 6
    assert kept.status == "Pending"

    # ------------------------------------------------
    # 5. Verify only ONE LLM call happened
    # ------------------------------------------------

    fake_structured_model.invoke.assert_called_once()

    # ------------------------------------------------
    # 6. Verify the complete batch reached the LLM
    # ------------------------------------------------

    prompt = fake_structured_model.invoke.call_args.args[0]

    assert "FOSSASIA" in prompt
    assert "Metaflow" in prompt

    assert "Python" in prompt
    assert "Agentic AI" in prompt
    assert "RAG" in prompt
    assert "LLM" in prompt
    assert "LLM-INFERENCE" in prompt
    assert "Backend" in prompt