from models import Organisation_entry
from db.engine import sessionLocal

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

db=sessionLocal()
try:
    for org in organisations:
        exsisting=(
            db.query(Organisation_entry).filter(Organisation_entry.org_name==org).first()
        )
        if exsisting: 
            print(f"{org} is already exsisting in the db")
            continue
        organisation=Organisation_entry(
            org_name=org
        )
        db.add(organisation)
    db.commit()
    print(f"\nOrganisations are added")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()





