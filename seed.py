from faker import Faker
from libgravatar import Gravatar

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from random import randint, choice
from passlib.context import CryptContext

from src.models import Contact, Email, Phone, Base, User


postgres = 'postgresql+psycopg2://postgres:29an99fr@192.168.1.242:5432/db_contacts'


engine = create_engine(postgres)
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

fake = Faker()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users = []
for j in range(15):
    pwd = fake.password(length=8)
    print(pwd)
    users.append(User(username=fake.name(),
                      email=fake.ascii_free_email(),
                      password=pwd_context.hash(pwd),
                      ))

session.add_all(users)


for i in range(100):
    phones = []
    emails = []
    for _ in range(randint(0, 4)):
        phones.append(Phone(number=fake.phone_number()))
    for _ in range(randint(0, 4)):
        emails.append(Email(address=fake.ascii_free_email()))

    session.add(Contact(first_name=fake.first_name(),
                        last_name=fake.last_name() if randint(0, 100) > 10 else None,
                        owner=choice(users),
                        emails=emails,
                        phones=phones,
                        birthday=fake.date_of_birth() if randint(0, 100) > 30 else None,
                        description=fake.sentence(nb_words=10, variable_nb_words=False) if randint(0, 100) < 30 else None))
    print(i)

session.commit()
session.close()

# r^n7uqIg
# +t6IrFag
# $i8QjIw&
# $2N4IwAv
# @V6K3*$u
# !s2Fj$++
# 4)Q2FFys
# 2&v@0wHw
# $8D+PcNl
# +3L0eMnp
# _4UOk@nS
# ($a4y1Kz
# +6A5Ycj#
# &9WYjXYN
# (89WBMb7
