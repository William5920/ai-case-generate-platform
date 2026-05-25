import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base


class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(String(64), primary_key=True, default=lambda: f"file-{uuid.uuid4().hex[:8]}")
    user_id = Column(String(64), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_type = Column(String(100))
    purpose = Column(String(20), nullable=False, default="requirement")
    created_at = Column(DateTime, default=datetime.utcnow)

    requirement = relationship("Requirement", back_populates="file_info", uselist=False)


class Requirement(Base):
    __tablename__ = "requirements"

    id = Column(String(64), primary_key=True, default=lambda: f"req-{uuid.uuid4().hex[:8]}")
    user_id = Column(String(64), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    input_mode = Column(String(10), nullable=False, default="text")
    raw_content = Column(Text)
    file_id = Column(String(64), ForeignKey("uploaded_files.id"), nullable=True)
    template_id = Column(String(20), default="user-story")
    standardized_content = Column(Text)
    explore_data = Column(JSON, default=list)
    status = Column(String(20), default="pending")
    source = Column(String(50), default="standardization")
    quality_score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    file_info = relationship("UploadedFile", back_populates="requirement")
    explore_messages = relationship("ExploreMessage", back_populates="requirement", cascade="all, delete-orphan")
    adjust_messages = relationship("AdjustMessage", back_populates="requirement", cascade="all, delete-orphan")
    doc_versions = relationship("DocVersion", back_populates="requirement", cascade="all, delete-orphan")
    split_requirements = relationship("SplitRequirement", back_populates="requirement", cascade="all, delete-orphan")


class ExploreMessage(Base):
    __tablename__ = "explore_messages"

    id = Column(String(64), primary_key=True, default=lambda: f"em-{uuid.uuid4().hex[:8]}")
    requirement_id = Column(String(64), ForeignKey("requirements.id"), nullable=False, index=True)
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    dimension_key = Column(String(50))
    dimension_label = Column(String(50))
    quick_replies = Column(JSON, default=list)
    replied = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    requirement = relationship("Requirement", back_populates="explore_messages")


class AdjustMessage(Base):
    __tablename__ = "adjust_messages"

    id = Column(String(64), primary_key=True, default=lambda: f"am-{uuid.uuid4().hex[:8]}")
    requirement_id = Column(String(64), ForeignKey("requirements.id"), nullable=False, index=True)
    role = Column(String(10), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default="discussion")
    proposal_content = Column(Text)
    change_summary = Column(Text)
    confirmed = Column(Boolean, default=False)
    rejected = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    requirement = relationship("Requirement", back_populates="adjust_messages")


class DocVersion(Base):
    __tablename__ = "doc_versions"

    id = Column(String(64), primary_key=True, default=lambda: f"ver-{uuid.uuid4().hex[:8]}")
    requirement_id = Column(String(64), ForeignKey("requirements.id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    requirement = relationship("Requirement", back_populates="doc_versions")


class SplitRequirement(Base):
    __tablename__ = "split_requirements"

    id = Column(String(64), primary_key=True, default=lambda: f"sr-{uuid.uuid4().hex[:8]}")
    requirement_id = Column(String(64), ForeignKey("requirements.id"), nullable=False)
    text = Column(Text)
    content = Column(Text)
    order_index = Column(Integer, nullable=False, default=0)
    sort_order = Column(Integer, default=0)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requirement = relationship("Requirement", back_populates="split_requirements")
    test_points = relationship("TestPoint", back_populates="split_requirement", cascade="all, delete-orphan")


class TestPoint(Base):
    __tablename__ = "test_points"

    id = Column(String(64), primary_key=True, default=lambda: f"tp-{uuid.uuid4().hex[:8]}")
    split_requirement_id = Column(String(64), ForeignKey("split_requirements.id"), nullable=False)
    text = Column(Text, nullable=False)
    description = Column(Text)
    source = Column(String(10), default="AI")
    marked = Column(Boolean, default=False)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    split_requirement = relationship("SplitRequirement", back_populates="test_points")
    test_cases = relationship("TestCase", back_populates="test_point", cascade="all, delete-orphan")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(String(64), primary_key=True, default=lambda: f"tc-{uuid.uuid4().hex[:8]}")
    test_point_id = Column(String(64), ForeignKey("test_points.id"), nullable=False)
    text = Column(String(255), nullable=False)
    case_property = Column(String(10), default="正例")
    pre_condition = Column(Text)
    steps = Column(JSON, default=list)
    source = Column(String(10), default="AI")
    marked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    test_point = relationship("TestPoint", back_populates="test_cases")


class AISession(Base):
    __tablename__ = "ai_sessions"

    id = Column(String(64), primary_key=True, default=lambda: f"sess-{uuid.uuid4().hex[:8]}")
    requirement_id = Column(String(64), nullable=False)
    node_id = Column(String(64), nullable=False)
    node_type = Column(String(20), nullable=False)
    marked_node_ids = Column(JSON, default=list)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("AIMessage", back_populates="session", cascade="all, delete-orphan")


class AIMessage(Base):
    __tablename__ = "ai_messages"

    id = Column(String(64), primary_key=True, default=lambda: f"msg-{uuid.uuid4().hex[:8]}")
    session_id = Column(String(64), ForeignKey("ai_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("AISession", back_populates="messages")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String(64), primary_key=True, default=lambda: f"task-{uuid.uuid4().hex[:8]}")
    requirement_id = Column(String(64), nullable=False)
    status = Column(String(20), default="pending")
    progress = Column(Integer, default=0)
    progress_text = Column(String(255), default="")
    use_knowledge_base = Column(Boolean, default=False)
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
