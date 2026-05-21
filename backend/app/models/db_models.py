import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.core.database import Base

class Requirement(Base):
    __tablename__ = "requirements"
    
    id = Column(String(64), primary_key=True, default=lambda: f"req-{uuid.uuid4().hex[:8]}")
    user_id = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text)
    status = Column(String(20), default="pending")
    source = Column(String(50), default="standardization")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    split_requirements = relationship("SplitRequirement", back_populates="requirement", cascade="all, delete-orphan")

class SplitRequirement(Base):
    __tablename__ = "split_requirements"
    
    id = Column(String(64), primary_key=True, default=lambda: f"sr-{uuid.uuid4().hex[:8]}")
    requirement_id = Column(String(64), ForeignKey("requirements.id"), nullable=False)
    text = Column(Text, nullable=False)
    status = Column(String(20), default="pending")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
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
