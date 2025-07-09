# src/database/models.py
from sqlalchemy import (Column, Integer, String, DateTime, ForeignKey, JSON,
                        Float, BigInteger)
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(BigInteger, primary_key=True, comment="Telegram User ID")
    username = Column(String, nullable=True)
    role = Column(String, default='free', nullable=False)
    points = Column(Integer, default=0, nullable=False)
    vip_expires_at = Column(DateTime, nullable=True)
    
    progress = relationship("UserProgress", back_populates="user", uselist=False, cascade="all, delete-orphan")
    missions = relationship("UserMission", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    point_transactions = relationship("PointTransaction", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

class UserProgress(Base):
    __tablename__ = 'user_progress'
    
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    current_story_node = Column(String, nullable=True)
    unlocked_fragments = Column(JSON, default=list, nullable=False)
    diana_state = Column(String, default='Enigmática', nullable=False)
    dominant_archetype = Column(String, nullable=True)
    secondary_archetypes = Column(JSON, default=list, nullable=False)
    resonance_score = Column(Float, default=0.0, nullable=False)
    significant_interactions = Column(JSON, default=list, nullable=False)
    last_interaction_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="progress")

    def __repr__(self):
        return f"<UserProgress(user_id={self.user_id}, diana_state='{self.diana_state}')>"

class Mission(Base):
    __tablename__ = 'missions'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(String, nullable=False)
    reward_points = Column(Integer, nullable=False)
    
    users = relationship("UserMission", back_populates="mission")

    def __repr__(self):
        return f"<Mission(id={self.id}, name='{self.name}')>"

class UserMission(Base):
    __tablename__ = 'user_missions'
    
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    mission_id = Column(Integer, ForeignKey('missions.id'), primary_key=True)
    completed_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, primary_key=True)
    
    user = relationship("User", back_populates="missions")
    mission = relationship("Mission", back_populates="users")

    def __repr__(self):
        return f"<UserMission(user_id={self.user_id}, mission_id={self.mission_id})>"

class Achievement(Base):
    __tablename__ = 'achievements'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=False)
    
    users = relationship("UserAchievement", back_populates="achievement")

    def __repr__(self):
        return f"<Achievement(id={self.id}, name='{self.name}')>"

class UserAchievement(Base):
    __tablename__ = 'user_achievements'
    
    user_id = Column(BigInteger, ForeignKey('users.id'), primary_key=True)
    achievement_id = Column(Integer, ForeignKey('achievements.id'), primary_key=True)
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="users")

    def __repr__(self):
        return f"<UserAchievement(user_id={self.user_id}, achievement_id={self.achievement_id})>"

class PointTransaction(Base):
    __tablename__ = 'point_transactions'

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    points = Column(Integer, nullable=False)
    reason = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="point_transactions")

    def __repr__(self):
        return f"<PointTransaction(user_id={self.user_id}, points={self.points}, reason='{self.reason}')>"
