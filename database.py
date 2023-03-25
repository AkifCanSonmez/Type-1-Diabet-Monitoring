from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# POSTRESQL_DATABASE_URL = "postgresql://fnqnngdy:1_uGTYjYqGSVNEiiPdfZYIR5NlU8djeU@castor.db.elephantsql.com/fnqnngdy"
POSTRESQL_DATABASE_URL = 'postgresql://postgres:353535@localhost:5432/diabetes_tracker_db'

engine = create_engine(POSTRESQL_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
