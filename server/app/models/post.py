import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base


def utcnow():
    return datetime.now(timezone.utc)


class PostState(str, enum.Enum):
    drafted = "drafted"
    published = "published"
    deleted = "deleted"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    blog_id: Mapped[str] = mapped_column(String(36), ForeignKey("blogs.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False, default="")
    state: Mapped[str] = mapped_column(String(50), nullable=False, default=PostState.drafted.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)

    blog: Mapped["Blog"] = relationship("Blog", back_populates="posts")
