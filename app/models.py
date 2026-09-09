from datetime import datetime

from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import String

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
        index=True,
        nullable=False
    )

    value = Column(
        Float,
        nullable=False
    )

    unit = Column(
        String,
        nullable=False
    )

    timestamp = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )