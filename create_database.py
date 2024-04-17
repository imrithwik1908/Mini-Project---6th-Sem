from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
from sqlalchemy import Table


Base = declarative_base()
engine = create_engine('sqlite:///my_database1.db')
Base.metadata.create_all(engine)
__all__ = ["Base", "engine"]

# Sport Type table (optional, if needed)
class SportType(Base):
  __tablename__ = "sport_types"
  id = Column(Integer, primary_key=True)
  name = Column(String(length=50), nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    profileURL = Column(String(255))
    city = Column(String(50))
    state = Column(String(50))
    country = Column(String(50))
    sex = Column(String(10), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    mobile_num = Column(String(20), unique=True)
    email = Column(String(255), nullable=False, unique=True)

    # One user to one comment (optional, replace with many-to-one if needed)
    comment = relationship("Comment", uselist=False, backref="user")  

    # Relationship with activities (many-to-many)
    activities = relationship("Activity", secondary="user_activity")

    # Relationship with challenges (many-to-many)
    challenges = relationship("Challenge", secondary="user_challenge")

    # Relationship with clubs (many-to-many)
    clubs = relationship("Club", secondary="user_club")

    # Relationship with shares (one-to-many)
    shares = relationship("Share", backref="user")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    dist = Column(Float, nullable=False)
    moving_time = Column(Integer, nullable=False)
    elapsed_time = Column(Integer, nullable=False)
    total_elevation_gain = Column(Float)
    elevation_high = Column(Float)
    elevation_low = Column(Float)
    sport_type_id = Column(Integer, ForeignKey("sport_types.id"))  # Optional foreign key if using SportType table
    start_date = Column(DateTime, nullable=False)
    start_date_local = Column(DateTime)
    timezone = Column(String(length=50))
    start_latlng = Column(String)
    end_latlng = Column(String)
    avg_speed = Column(Float)
    max_speed = Column(Float)
    private = Column(Boolean, nullable=False)
    likes = Column(Integer, nullable=False)

    # Relationship with comments (many-to-many)
    comments = relationship("Comment", secondary="activity_comment", overlaps="activities")

    # Relationship with shares (one-to-many)
    shares = relationship("Share", backref="activity")

class Club(Base):
    __tablename__ = "clubs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=255), nullable=False)
    profile_medium = Column(String(length=255))
    city = Column(String(50))
    state = Column(String(50))
    country = Column(String(50))
    cover_photo = Column(String(length=255))
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    verified = Column(Boolean, nullable=False)

    # Relationship with challenges (one-to-many)
    challenges = relationship("Challenge", backref="club")

    # Relationship with shares (one-to-many)
    shares = relationship("Share", backref="club")

    # Relationship with users (many-to-many)
    members = relationship("User", secondary="user_club", overlaps="clubs")

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=255), nullable=False)
    start_date = Column(DateTime, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    activity_type = Column(String(length=50), nullable=False)
    description = Column(Text)
    complete = Column(Boolean, nullable=False)

    # One challenge to one leaderboard (optional, replace with one-to-many if needed)
    leadership = relationship("Leadership", uselist=False, back_populates="challenge")

    # Relationship with activities (many-to-many)
    activities = relationship("Activity", secondary="challenge_activity")

    # Relationship with clubs (one-to-many)
    club_id = Column(Integer, ForeignKey("clubs.id"))

    # Relationship with shares (one-to-many)
    shares = relationship("Share", backref="challenge")

class Leadership(Base):  # Leadership table for challenge leaderboard
    __tablename__ = "leadership"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # Add columns for leaderboard data (e.g., rank, points, time)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)

    # Relationship with Challenge (one-to-one)
    challenge = relationship("Challenge", back_populates="leadership")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

    # Relationship with activities (many-to-many)
    activities = relationship("Activity", secondary="activity_comment", overlaps="comments")

    # Relationship with challenges (many-to-many)
    challenges = relationship("Challenge", secondary="challenge_comment")

class Share(Base):
    __tablename__ = "shares"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(length=255))
    email = Column(String(length=255))  # Optional email for sharing
    created_at = Column(DateTime, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationship with activities (one-to-many)
    activity_id = Column(Integer, ForeignKey("activities.id"))

    # Relationship with challenges (one-to-many)
    challenge_id = Column(Integer, ForeignKey("challenges.id"))

    # Relationship with clubs (one-to-many)
    club_id = Column(Integer, ForeignKey("clubs.id"))

# Many-to-many association tables
user_activity = relationship("User", secondary="user_activity")
user_activity_table = Table(
    "user_activity",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("activity_id", Integer, ForeignKey("activities.id")),
)

user_challenge = relationship("User", secondary="user_challenge")
user_challenge_table = Table(
    "user_challenge",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("challenge_id", Integer, ForeignKey("challenges.id")),
)

user_club = relationship("User", secondary="user_club")
user_club_table = Table(
    "user_club",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("club_id", Integer, ForeignKey("clubs.id")),
)

challenge_activity = relationship("Challenge", secondary="challenge_activity")
challenge_activity_table = Table(
    "challenge_activity",
    Base.metadata,
    Column("challenge_id", Integer, ForeignKey("challenges.id")),
    Column("activity_id", Integer, ForeignKey("activities.id")),
)

activity_comment = relationship("Activity", secondary="activity_comment")
activity_comment_table = Table(
    "activity_comment",
    Base.metadata,
    Column("activity_id", Integer, ForeignKey("activities.id")),
    Column("comment_id", Integer, ForeignKey("comments.id")),
)

# Challenge comment association table (many-to-many)
challenge_comment = relationship("Challenge", secondary="challenge_comment")
challenge_comment_table = Table(
    "challenge_comment",
    Base.metadata,
    Column("challenge_id", Integer, ForeignKey("challenges.id")),
    Column("comment_id", Integer, ForeignKey("comments.id")),
)




