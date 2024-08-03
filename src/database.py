from sqlmodel import SQLModel, create_engine
import os

data_dir = '/data'
sqlite_file = os.path.join(data_dir, 'database.db')
sqlite_url = f"sqlite:///{sqlite_file}"

engine = create_engine(sqlite_url, echo=True)