from sqlalchemy import create_engine, Column, Integer, String, DateTime, UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from secure_pass import secure_the_password
from schemas import UserLogin
# Define the SQLite database URL
DATABASE_URL = "sqlite:////home/ajay-netweb/PycharmProjects/keycloak/skylus.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, echo=True)

# Create a declarative base class
Base = declarative_base()
# Base.metadata.reflect(engine)
Base.metadata.create_all(engine)


class UserLoginTable(Base):
    __tablename__ = 'user_login'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(200))
    domain_name = Column(String(200))


# Create a session factory
Session = sessionmaker(bind=engine, autoflush=False,autocommit=False)
session = Session()


def select_user(username: str):
    try:
        user = session.query(UserLoginTable).filter_by(username=username).first()
        if user:
            return user
        return False
    except Exception as e:
        return False


def insert_user(username: str, password: str, domain_name: str):
    try:
        # encrpty_pass = secure_the_password.encrypt_password(password)
        new_user = UserLoginTable(username=username, password=password, domain_name=domain_name)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return True
    except Exception as e:
        return False
