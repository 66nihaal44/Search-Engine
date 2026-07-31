from sqlalchemy import Column, Integer, String
from engine import Base, init_db

class Page(Base):
  __tablename__ = "pages"
  url = Column(String, primary_key=True)
  title = Column(String, nullable=False)
  textcontent = Column(String, nullable=False)

init_db()
