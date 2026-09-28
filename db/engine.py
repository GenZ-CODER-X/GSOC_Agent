from sqlalchemy import create_engine,text,inspect
from sqlalchemy.orm import sessionmaker,declarative_base
from core import config
from db.database import Base

db_url=config.settings.db_url
engine=create_engine(db_url)


sessionLocal=sessionmaker(bind=engine,autocommit=False,autoflush=False)

def get_db():
    print("Waiting for connection")
    db=sessionLocal()
    try:
        print("Connecting to db")
        yield db
        print("Connected to db")
    finally:
        db.close()
if __name__ == "__main__":
    import models
    print("Models registered:")
    print(list(Base.metadata.tables.keys()))

    Base.metadata.create_all(bind=engine)

    print("Tables visible after creation:")
    print(inspect(engine).get_table_names())

    print("All tables created successfully!")