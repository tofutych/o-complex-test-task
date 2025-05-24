import uuid

from sqlalchemy import MetaData
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from src.core import settings
from src.utils import camel_case_to_snake_case


class Base(DeclarativeBase):
    __abstract__ = True  # pyright: ignore [reportUnannotatedClassAttribute]

    metadata = MetaData(naming_convention=settings.NAMING_CONVENTION)  # pyright: ignore [reportUnannotatedClassAttribute]

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{camel_case_to_snake_case(cls.__name__)}s"
