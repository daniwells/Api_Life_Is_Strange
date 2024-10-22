from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config

SQLALCHEMY_DATABASE_URL = (
    config("DATABASE_URL")
)

# Cria uma instânica da conexão com o banco. Responsável por gerenciar os requisições e interações.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Interface para que o usuário possa interagir com o usuário. Responsável pelas transações, persistência de objetos e consultas
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Cria uma classe base a criaão de modelos. É a classe a qual todas as outras serão geradas
Base = declarative_base()