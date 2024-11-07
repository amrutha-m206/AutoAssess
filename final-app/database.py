from sqlalchemy import create_engine, Column, Integer, Text, String, ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database setup
DATABASE_URL = "sqlite:///quiz_data.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()


# Quiz table to store generated questions and answers
class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True)
    question = Column(Text)
    option_a = Column(String)
    option_b = Column(String)
    option_c = Column(String)
    option_d = Column(String)
    correct_answer = Column(String)


# Create the database
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


# Function to store quiz questions in database
def add_quiz(question, options, correct_answer):
    session = Session()
    quiz = Quiz(
        question=question,
        option_a=options[0],
        option_b=options[1],
        option_c=options[2],
        option_d=options[3],
        correct_answer=correct_answer,
    )
    session.add(quiz)
    session.commit()
    session.close()


# Function to get all quizzes
def get_quizzes():
    session = Session()
    quizzes = session.query(Quiz).all()
    session.close()
    return quizzes
