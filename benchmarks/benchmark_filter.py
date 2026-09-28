import json
import time

from org_info.org_structured_info import gsoc_org_page
from agents.filter_org import build_filter_input
from langchain_google_genai import ChatGoogleGenerativeAI
from core import config
from schemas import filter_agent


def benchmark_filter():

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

    my_skills = [
        "Python",
        "Agentic AI",
        "RAG",
        "LLM",
        "LLM-INFERENCE",
        "Backend",
    ]

    total_start = time.perf_counter()

    # =========================================
    # 1. GSoC API + organization matching
    # =========================================

    api_start = time.perf_counter()

    org_info = gsoc_org_page.get_org_details_gsoc_page(
        organisations
    )

    api_end = time.perf_counter()

    # =========================================
    # 2. BUILD LIGHTWEIGHT FILTER INPUT
    # =========================================

    projection_start = time.perf_counter()

    filter_input = build_filter_input(org_info)

    projection_end = time.perf_counter()

    # =========================================
    # 3. SERIALIZE DATA FOR PROMPT
    # =========================================

    serialization_start = time.perf_counter()

    full_source_json = json.dumps(
        org_info,
        indent=2
    )

    filter_json = json.dumps(
        filter_input,
        indent=2
    )

    serialization_end = time.perf_counter()

    # =========================================
    # 4. MODEL SETUP
    # =========================================

    model_start = time.perf_counter()

    model = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        google_api_key=config.settings.gemini_api_key,
        temperature=0,
    )

    structured_model = model.with_structured_output(
        filter_agent.FilterOrgBatchOutput
    )

    model_end = time.perf_counter()

    # =========================================
    # 5. PROMPT CONSTRUCTION
    # =========================================

    prompt_start = time.perf_counter()

    prompt = f"""
You are a GSoC organization filtering agent.

Student skills:
{my_skills}

The following is a batch of GSoC organizations retrieved from
the GSoC API.

Organization data:
{filter_json}

Task:

1. Compare each organization's technologies, topics, description,
and category against the student's skills.

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
7. Preserve organization names exactly as provided.
8. Return every organization exactly once.
"""

    prompt_end = time.perf_counter()

    # =========================================
    # 6. REAL LLM CALL
    # =========================================

    llm_start = time.perf_counter()

    result = structured_model.invoke(prompt)

    llm_end = time.perf_counter()

    total_end = time.perf_counter()

    # =========================================
    # 7. BENCHMARK OUTPUT
    # =========================================

    print("\n==========================================")
    print("       REAL-TIME FILTER BENCHMARK")
    print("==========================================")

    print("\n--- Organizations ---")

    print(
        f"Organizations requested : {len(organisations)}"
    )

    print(
        f"Organizations matched   : {len(org_info)}"
    )

    print("\n--- Data Size ---")

    print(
        f"Full source characters  : "
        f"{len(full_source_json):,}"
    )

    print(
        f"Full source KB          : "
        f"{len(full_source_json) / 1024:.2f} KB"
    )

    print(
        f"Filter JSON characters  : "
        f"{len(filter_json):,}"
    )

    print(
        f"Filter JSON KB          : "
        f"{len(filter_json) / 1024:.2f} KB"
    )

    print(
        f"Data reduction          : "
        f"{100 * (1 - len(filter_json) / len(full_source_json)):.2f}%"
    )

    print(
        f"Prompt characters       : "
        f"{len(prompt):,}"
    )

    print(
        f"Prompt KB               : "
        f"{len(prompt) / 1024:.2f} KB"
    )

    print("\n--- Timing ---")

    print(
        f"GSoC API + matching     : "
        f"{api_end - api_start:.4f} sec"
    )

    print(
        f"Filter projection       : "
        f"{projection_end - projection_start:.4f} sec"
    )

    print(
        f"JSON serialization      : "
        f"{serialization_end - serialization_start:.4f} sec"
    )

    print(
        f"Model setup             : "
        f"{model_end - model_start:.4f} sec"
    )

    print(
        f"Prompt construction     : "
        f"{prompt_end - prompt_start:.4f} sec"
    )

    print(
        f"LLM inference           : "
        f"{llm_end - llm_start:.4f} sec"
    )

    print("------------------------------------------")

    print(
        f"TOTAL                   : "
        f"{total_end - total_start:.4f} sec"
    )

    print("\n--- Result ---")

    print(
        f"Discarded organizations : "
        f"{len(result.discarded_organizations)}"
    )

    print(
        f"Kept organizations      : "
        f"{len(result.organizations)}"
    )

    # =========================================
    # 8. TOKEN USAGE
    # =========================================

    usage = getattr(result, "usage_metadata", None)

    if usage:
        print("\n--- Token Usage ---")

        print(
            f"Input tokens            : "
            f"{usage.get('input_tokens')}"
        )

        print(
            f"Output tokens           : "
            f"{usage.get('output_tokens')}"
        )

        print(
            f"Total tokens            : "
            f"{usage.get('total_tokens')}"
        )


if __name__ == "__main__":
    benchmark_filter()