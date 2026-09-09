from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float

from app.db import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    metric = Column(
        String,
        index=True
    )

    value = Column(
        Float
    )

    unit = Column(
        String
    )