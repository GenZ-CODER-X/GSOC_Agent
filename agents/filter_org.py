import time,json
from db.database import SessionLocal
from org_info.org_structured_info import gsoc_org_page
from langchain_openrouter import ChatOpenRouter
from core import config
from schemas import filter_agent
from models import Organisation_entry, Organisation, Discard_org


def build_filter_input(org_info: dict) -> dict:
    filter_input = {}

    for org_name, org in org_info.items():
        filter_input[org_name] = {
            "description": org.get("description"),
            "category": org.get("category"),
            "technologies": org.get("technologies", []),
            "topics": org.get("topics", []),
        }
    return filter_input

def filter_org():
    organisations = [
    "FOSSASIA",
    "Alaska",
    "ML4LAM",
    "Accord Project",
    "MoFA",
    "Metaflow",
    "Kubeflow",
    "Project MESA",
    "DeepChem",
    "Gemini CLI",
    "OpenVINO Toolkit",
    "HumanAI",
    "CERN-HSF",
    "Open Genome Informatics",
    "Rocket.Chat",
    "JabRef",
    "INCF",
    "The Libreswan Project"
]
    # organizations=db.query(Organisation_entry).all()
    my_skills = [
        "Python",
        "Agentic AI",
        "RAG",
        "LLM",
        "LLM-INFERENCE",
        "Backend"
    ]

    org_info = gsoc_org_page.get_org_details_gsoc_page(organisations)
    filter_input = build_filter_input(org_info)
    
    model = ChatOpenRouter(
        model="~openai/gpt-sol-latest",
        api_key=config.settings.openrouter_api_key,
        temperature=0,
        max_tokens=1200,
    )

    structured_model = model.with_structured_output(
        filter_agent.FilterOrgBatchOutput,
        method="json_schema",
    )
    prompt = f"""
    You are a GSoC organization filtering agent.

    Student skills:
    {my_skills}

    The following is a batch of GSoC organizations retrieved from
    the GSoC API.

    Organization data:
    {json.dumps(filter_input, indent=2)}

    Your goal is to perform a first-stage candidate filter.

    The purpose of this filter is NOT to determine whether the student
    is fully qualified for an organization.

    The purpose is to remove organizations whose CORE technical work is
    clearly unrelated to the student's profile, while preserving
    organizations that have meaningful technical alignment even when
    the student has some missing skills.

    IMPORTANT DECISION RULES:

    1. Evaluate the organization's CORE technical work using its
    description, technologies, topics, and category.

    2. KEEP an organization when its core work has a direct or
    reasonably close relationship to the student's skills.

    3. Missing skills are NOT a reason to discard an organization when
    the organization's core work is otherwise relevant.

    4. A technology gap is acceptable when the organization is otherwise
    relevant to the student's profile.

    5. Do NOT keep an organization merely because it:
    - uses programming
    - uses open source
    - uses Linux
    - uses C/C++
    - uses Python
    - involves software engineering
    - involves systems
    - involves networking
    - has a backend
    These are NOT sufficient by themselves.

    6. Generic technical similarity is NOT enough.
    The organization's CORE domain must have meaningful overlap with
    the student's technical profile.

    7. KEEP organizations whose core work is related to areas such as:
    - AI / ML
    - LLMs
    - RAG
    - AI agents / Agentic AI
    - model inference or serving
    - Python-based software
    - backend systems
    - APIs / web services
    - databases / data engineering
    - cloud or infrastructure that is directly relevant to
        backend or AI systems

    8. DISCARD organizations whose CORE work belongs to a substantially
    different specialization and has no meaningful overlap with the
    student's profile.

    9. Examples of substantially different specialization include
    organizations primarily focused on areas such as:
    - VPN / IPsec / network security protocols
    - specialized hardware
    - embedded systems
    - graphics rendering
    - telecommunications
    - unrelated scientific domains
    - unrelated hardware/software domains

    Do not discard merely because a technology is unfamiliar;
    discard because the CORE problem/domain is unrelated.

    10. Before deciding, answer this question:

    "What specific part of this organization's CORE technical work
        matches the student's skills?"

    If you can identify a meaningful match → KEEP.

    If the only match is generic programming or general software
    engineering → DISCARD.

    11. Do not assume the organization must match every student skill.
        Partial alignment is acceptable.

    12. Do not judge whether the student would be selected or qualified.
        Only determine whether the organization belongs in the candidate
        pool for further research.

    13. If information is incomplete:
        - KEEP when there is already evidence of meaningful alignment.
        - DISCARD only when the available information clearly indicates
        that the organization's core work is unrelated.

    14. Do not invent information.

    15. Use ONLY the supplied organization data and the student's skills.

    16. Preserve the organization name exactly as provided.

    17. Return EVERY supplied organization exactly once.

    Task:

    1. Compare each organization's:
    - description
    - category
    - technologies
    - topics

    against the student's skills.

    2. Place relevant organizations in organizations.

    3. Place clearly unrelated organizations in
    discarded_organizations.

    4. For each discarded organization:
    - provide the organization name
    - provide its technology stack when available
    - provide missing skills only when supported by the supplied data
    - explain why its CORE technical work is not sufficiently related

    5. For organizations that are kept, do not provide unnecessary
    explanations. Only return the organization name.

    FINAL DECISION RULE:

    KEEP  = meaningful CORE technical/domain overlap,
            even if some skills are missing.

    DISCARD = CORE technical/domain mismatch,
            even if the organization uses general programming,
            open source, Linux, systems, or networking.

    Do not optimize for maximum recall at the expense of obvious
    domain mismatches.

    The goal is:
        remove clearly irrelevant organizations
        +
        preserve organizations with genuine technical alignment.
    """
    try:
        result = structured_model.invoke(prompt)
    except Exception as e:
        print("\n===== OPENROUTER ERROR =====")
        print(type(e))
        print(e)
        print(getattr(e, "response", None))
        print(getattr(e, "body", None))
        raise
    save_filter_result(result)
    return result

def save_filter_result(result):
    db = SessionLocal()

    try:
        # Get all entries once
        entries = db.query(Organisation_entry).all()

        # Map organization name -> Organisation_entry
        entry_map = {
            entry.org_name: entry
            for entry in entries
        }

        # ---------------------------------------------------
        # SAVE ACCEPTED ORGANIZATIONS
        # ---------------------------------------------------

        for org in result.organizations:
            org_name = org.org_name

            entry = entry_map.get(org_name)

            if entry is None:
                print(f"WARNING: {org_name} not found in organisations_entry")
                continue

            # Remove from discard_orgs if it was previously discarded
            existing_discard = (
                db.query(Discard_org)
                .filter(Discard_org.user_entry_id == entry.id)
                .first()
            )

            if existing_discard:
                db.delete(existing_discard)

            # Check whether it already exists
            existing_org = (
                db.query(Organisation)
                .filter(Organisation.user_entry_id == entry.id)
                .first()
            )

            if existing_org:
                print(f"Already exists in organisations: {org_name}")
            else:
                new_org = Organisation(
                    org_name=org_name,
                    user_entry_id=entry.id,
                    status="Pending",
                )

                db.add(new_org)

                print(f"Added to organisations: {org_name}")

        # ---------------------------------------------------
        # SAVE DISCARDED ORGANIZATIONS
        # ---------------------------------------------------

        for org in result.discarded_organizations:
            org_name = org.org_name

            entry = entry_map.get(org_name)

            if entry is None:
                print(f"WARNING: {org_name} not found in organisations_entry")
                continue

            # Remove from organisations if it was previously accepted
            existing_org = (
                db.query(Organisation)
                .filter(Organisation.user_entry_id == entry.id)
                .first()
            )

            if existing_org:
                db.delete(existing_org)

            # Check whether it already exists
            existing_discard = (
                db.query(Discard_org)
                .filter(Discard_org.user_entry_id == entry.id)
                .first()
            )

            if existing_discard:
                # Update existing record
                existing_discard.org_name = org_name
                existing_discard.Tech_stack_org = org.Tech_stack_org
                existing_discard.missing_skills = org.missing_skills
                existing_discard.reason = org.reason

                print(f"Updated discard_orgs: {org_name}")

            else:
                new_discard = Discard_org(
                    org_name=org_name,
                    user_entry_id=entry.id,
                    Tech_stack_org=org.Tech_stack_org,
                    missing_skills=org.missing_skills,
                    reason=org.reason,
                )

                db.add(new_discard)

                print(f"Added to discard_orgs: {org_name}")

        # Save everything
        db.commit()

        print("\nFilter results saved successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error while saving filter results: {e}")
        raise

    finally:
        db.close()

if __name__ == "__main__":
    result = filter_org()

    print("\n===== KEPT =====")
    for org in result.organizations:
        print(org)

    print("\n===== DISCARDED =====")
    for org in result.discarded_organizations:
        print(f"\n{org}")