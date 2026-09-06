from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Zajednicki predak svih modela.

    Drzi registar tabela u Base.metadata - Alembic gleda bas njega
    da vidi kako shema treba da izgleda.
    """


class Company(Base):
    __tablename__ = "company"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="company")


class Location(Base):
    __tablename__ = "location"

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    area: Mapped[Optional[list]] = mapped_column(JSONB)
    latitude: Mapped[Optional[float]]
    longitude: Mapped[Optional[float]]

    # ostaju prazne do Phase 2, kad se izvuku iz display_name / area
    city: Mapped[Optional[str]] = mapped_column(String(120))
    region: Mapped[Optional[str]] = mapped_column(String(120))

    jobs: Mapped[list["Job"]] = relationship(back_populates="location")


class RawJob(Base):
    """Netaknut odgovor izvora - nikad se ne mijenja, sluzi za ponovnu obradu."""

    __tablename__ = "raw_job"
    __table_args__ = (
        UniqueConstraint("source", "source_job_id", name="uq_raw_job_source_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(32), index=True)
    source_job_id: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSONB)
    search_phrase: Mapped[Optional[str]] = mapped_column(String(120))
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Job(Base):
    """Normalizovan oglas - zajednicka polja iz svih izvora."""

    __tablename__ = "job"
    __table_args__ = (
        UniqueConstraint("source", "source_job_id", name="uq_job_source_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    source: Mapped[str] = mapped_column(String(32), index=True)
    source_job_id: Mapped[str] = mapped_column(String(64))

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(Text)

    company_id: Mapped[Optional[int]] = mapped_column(ForeignKey("company.id"), index=True)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("location.id"), index=True)

    salary_min: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    salary_max: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))

    salary_min_yearly: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    salary_max_yearly: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))

    salary_currency: Mapped[Optional[str]] = mapped_column(String(3))
    # 'yearly' ili 'monthly' - karriere.at ima oba, bez ovoga se plate ne smiju porediti
    salary_period: Mapped[Optional[str]] = mapped_column(String(16))
    salary_is_predicted: Mapped[Optional[bool]]

    employment_type: Mapped[Optional[str]] = mapped_column(String(32))
    employment_type_norm: Mapped[Optional[str]] = mapped_column(String(32))
    remote_option: Mapped[Optional[str]] = mapped_column(String(32))
    category_label: Mapped[Optional[str]] = mapped_column(String(120))

    duplicate_of : Mapped[Optional[str]] = mapped_column(String(32))

    url: Mapped[Optional[str]] = mapped_column(Text)

    posted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), index=True)
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    company: Mapped[Optional["Company"]] = relationship(back_populates="jobs")
    location: Mapped[Optional["Location"]] = relationship(back_populates="jobs")
