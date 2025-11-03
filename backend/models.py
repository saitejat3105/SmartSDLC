from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    histories = relationship("History", back_populates="user")
    challenges = relationship("ChallengeAttempt", back_populates="user")

class History(Base):
    __tablename__ = "histories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    request_type = Column(String)  # code, test_cases, bug_fix, requirements_to_code
    input_text = Column(Text)
    output_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="histories")

class CodingProblem(Base):
    __tablename__ = "coding_problems"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    difficulty = Column(String)  # Easy, Medium, Hard
    language = Column(String)  # Python, Java
    test_cases = Column(Text)  # JSON string
    solution = Column(Text)  # Hidden from users
    
    attempts = relationship("ChallengeAttempt", back_populates="problem")

class ChallengeAttempt(Base):
    __tablename__ = "challenge_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem_id = Column(Integer, ForeignKey("coding_problems.id"))
    code = Column(Text)
    language = Column(String)
    passed = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="challenges")
    problem = relationship("CodingProblem", back_populates="attempts")