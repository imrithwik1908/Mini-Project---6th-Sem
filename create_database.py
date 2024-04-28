from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship

Base = declarative_base()
engine = create_engine('sqlite:///my_database1.db')
Base.metadata.create_all(engine)
__all__ = ["Base", "engine"]

class SportType(Base):
    __tablename__ = "sport_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(length=50))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    profileURL = Column(String(255))
    city = Column(String(50))
    state = Column(String(50))
    country = Column(String(50))
    sex = Column(String(10))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    mobile_num = Column(String(20), unique=True)
    email = Column(String(255), unique=True)

    comment = relationship("Comment", backref="user")
    activities = relationship("Activity", secondary="user_activity_table", backref="users")
    challenges = relationship("Challenge", secondary="user_challenge_table", backref="users")
    clubs = relationship("Club", secondary="user_club_table", backref="users")
    shares = relationship("Share", backref="user")

class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255))
    dist = Column(Float)
    moving_time = Column(Integer)
    elapsed_time = Column(Integer)
    total_elevation_gain = Column(Float)
    elevation_high = Column(Float)
    elevation_low = Column(Float)
    sport_type_id = Column(Integer, ForeignKey("sport_types.id"))  
    start_date = Column(DateTime)
    start_date_local = Column(DateTime)
    timezone = Column(String(length=50))
    start_latlng = Column(String)
    end_latlng = Column(String)
    avg_speed = Column(Float)
    max_speed = Column(Float)
    private = Column(Boolean)
    likes = Column(Integer)

    comments = relationship("Comment", secondary="activity_comment_table", backref="activities")
    shares = relationship("Share", backref="activity")

class Club(Base):
    __tablename__ = "clubs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=255))
    profile_medium = Column(String(length=255))
    city = Column(String(50))
    state = Column(String(50))
    country = Column(String(50))
    cover_photo = Column(String(length=255))
    admin_id = Column(Integer, ForeignKey("users.id"), )
    verified = Column(Boolean, )

    challenges = relationship("Challenge", backref="club")
    shares = relationship("Share", backref="club")
    members = relationship("User", secondary="user_club_table", backref="clubs")

class Challenge(Base):
    __tablename__ = "challenges"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(length=255), )
    start_date = Column(DateTime)
    start_time = Column(DateTime)
    end_date = Column(DateTime)
    end_time = Column(DateTime)
    activity_type = Column(String(length=50))
    description = Column(Text)
    complete = Column(Boolean)

    leadership = relationship("Leadership", backref="challenge")
    activities = relationship("Activity", secondary="challenge_activity_table", backref="challenges")
    club_id = Column(Integer, ForeignKey("clubs.id"))
    shares = relationship("Share", backref="challenge")

class Leadership(Base):  
    __tablename__ = "leadership"
    id = Column(Integer, primary_key=True, autoincrement=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    challenge = relationship("Challenge", backref="leaderboard", uselist=False)

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    comment_text = Column(String(255))
    created_at = Column(DateTime)

    activities = relationship("Activity", secondary="activity_comment_table", backref="comments")
    challenges = relationship("Challenge", secondary="challenge_comment_table", backref="comments")

class Share(Base):
    __tablename__ = "shares"
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(length=255))
    email = Column(String(length=255))  
    created_at = Column(DateTime)
    user_id = Column(Integer, ForeignKey("users.id"))
    activity_id = Column(Integer, ForeignKey("activities.id"))
    challenge_id = Column(Integer, ForeignKey("challenges.id"))
    club_id = Column(Integer, ForeignKey("clubs.id"))

user_activity_table = Table(
    "user_activity_table",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("activity_id", Integer, ForeignKey("activities.id")),
)

user_challenge_table = Table(
    "user_challenge_table",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("challenge_id", Integer, ForeignKey("challenges.id"), primary_key=True)
)

user_club_table = Table(
    "user_club_table",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("club_id", Integer, ForeignKey("clubs.id"), primary_key=True)
)

challenge_activity_table = Table(
    "challenge_activity_table",
    Base.metadata,
    Column("challenge_id", Integer, ForeignKey("challenges.id"), primary_key=True),
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True)
)

activity_comment_table = Table(
    "activity_comment_table",
    Base.metadata,
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True),
    Column("comment_id", Integer, ForeignKey("comments.id"), primary_key=True)
)

challenge_comment_table = Table(
    "challenge_comment_table",
    Base.metadata,
    Column("challenge_id", Integer, ForeignKey("challenges.id"), primary_key=True),
    Column("comment_id", Integer, ForeignKey("comments.id"), primary_key=True)
)





