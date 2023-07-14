from faker import Faker

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from random import randint, choice

from src.models import Contact, Email, Phone, Base, User


postgres = 'postgresql+psycopg2://postgres:29an99fr@192.168.1.242:5432/db_contacts'


engine = create_engine(postgres)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)


if __name__ == "__main__":
    session = Session()
    user = session.query(User).filter(User.id == 1).first()
    print(user)
    session.close()
