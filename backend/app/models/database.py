"""SQLAlchemy database models."""

import json
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(50), nullable=False)
    input_type = Column(String(50), nullable=False)
    input_value = Column(String(500), nullable=False)
    country = Column(String(10), default="US")
    currency = Column(String(10), default="USD")
    status = Column(String(50), default="completed")
    data_source = Column(String(20), default="mock")
    pricing_summary_json = Column(Text, default="{}")
    keyword_summary_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    listings = relationship("Listing", back_populates="analysis", cascade="all, delete-orphan")
    competitors = relationship("Competitor", back_populates="analysis", cascade="all, delete-orphan")
    listing_issues = relationship("ListingIssue", back_populates="analysis", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="analysis", cascade="all, delete-orphan")
    trends = relationship("Trend", back_populates="analysis", cascade="all, delete-orphan")


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    platform = Column(String(50), nullable=False)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), default="")
    shop_name = Column(String(200), default="")
    price = Column(Float, default=0.0)
    currency = Column(String(10), default="USD")
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    image_url = Column(String(1000), default="")
    description = Column(Text, default="")
    tags_json = Column(Text, default="[]")
    detected_keywords_json = Column(Text, default="[]")
    raw_data_json = Column(Text, default="{}")

    analysis = relationship("Analysis", back_populates="listings")
    created_at = Column(DateTime, default=datetime.utcnow)

    @property
    def tags(self) -> list:
        return json.loads(self.tags_json or "[]")

    @tags.setter
    def tags(self, value: list):
        self.tags_json = json.dumps(value)

    @property
    def detected_keywords(self) -> list:
        return json.loads(self.detected_keywords_json or "[]")

    @detected_keywords.setter
    def detected_keywords(self, value: list):
        self.detected_keywords_json = json.dumps(value)


class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    competitor_name = Column(String(200), nullable=False)
    platform = Column(String(50), nullable=False)
    product_count = Column(Integer, default=0)
    average_price = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    common_keywords_json = Column(Text, default="[]")
    positioning_summary = Column(Text, default="")

    analysis = relationship("Analysis", back_populates="competitors")

    @property
    def common_keywords(self) -> list:
        return json.loads(self.common_keywords_json or "[]")

    @common_keywords.setter
    def common_keywords(self, value: list):
        self.common_keywords_json = json.dumps(value)


class ListingIssue(Base):
    __tablename__ = "listing_issues"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=True)
    severity = Column(String(20), default="low")
    category = Column(String(100), default="")
    issue = Column(Text, default="")
    suggestion = Column(Text, default="")

    analysis = relationship("Analysis", back_populates="listing_issues")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    listing_id = Column(Integer, ForeignKey("listings.id"), nullable=True)
    category = Column(String(100), default="")
    recommendation = Column(Text, default="")
    reasoning = Column(Text, default="")
    confidence = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="recommendations")


class Trend(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    trend_name = Column(String(200), nullable=False)
    trend_type = Column(String(100), default="")
    evidence = Column(Text, default="")
    opportunity = Column(Text, default="")

    analysis = relationship("Analysis", back_populates="trends")


class CodexRun(Base):
    __tablename__ = "codex_runs"

    id = Column(Integer, primary_key=True, index=True)
    run_type = Column(String(100), nullable=False)
    platform = Column(String(50), default="")
    status = Column(String(50), default="completed")
    input_summary = Column(Text, default="")
    output_summary = Column(Text, default="")
    proposed_patch = Column(Text, default="")
    applied_patch = Column(Boolean, default=False)
    error_message = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
