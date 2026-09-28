import time,json
from db.database import SessionLocal
from org_info.org_structured_info import gsoc_org_page
from langchain_google_genai import ChatGoogleGenerativeAI
from core import config
from schemas import filter_agent
from models import Organisation_entry

db=SessionLocal()

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

    model = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        google_api_key=config.settings.gemini_api_key,
        temperature=0,
    )

    structured_model = model.with_structured_output(
        filter_agent.FilterOrgBatchOutput
    )

    prompt = f"""
    You are a GSoC organization filtering agent.

    Student skills:
    {my_skills}

    The following is a batch of GSoC organizations retrieved from
    the GSoC API.

    Organization data:
    {json.dumps(filter_input,indent=2)}

    Task:

    1. Compare each organization's technologies, topics, description,
    and other available information against the student's skills.

    2. If an organization has no meaningful relationship to the
    student's skills, place it in discarded_organizations.

    3. For discarded organizations:
    - provide the organization name
    - provide its technology stack when available
    - provide the student's missing/relevant skills
    - explain why it was discarded

    4. If an organization has meaningful alignment, place it in
    organizations.

    5. Do not invent information.
    6. Use only the supplied organization data and student skills.
    7. Preserve the organization name exactly as provided.
    8. Return every organization exactly once.
    """

    result = structured_model.invoke(prompt)

    print(result)
    return result

if __name__ == "__main__":
    result = filter_org()

    print("\n===== KEPT =====")
    for org in result.organizations:
        print(org)

    print("\n===== DISCARDED =====")
    for org in result.discarded_organizations:
        print(f"\n{org}")