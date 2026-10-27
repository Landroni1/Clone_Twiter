from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class TweetMedia(Base):
    """
    Модель загруженного медиафайла (изображения).
    """

    __tablename__ = "tweet_media"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(500), nullable=False)
    tweet_id = Column(
        Integer, ForeignKey("tweets.id", ondelete="CASCADE"), nullable=True, index=True
    )

    tweet = relationship("Tweet", back_populates="media")
