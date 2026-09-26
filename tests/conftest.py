import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.services.db import Base


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    yield session
    session.close()
