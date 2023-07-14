from faker import Faker
from libgravatar import Gravatar

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from random import randint, choice
from passlib.context import CryptContext

from src.models import Contact, Email, Phone, Base, User


postgres = ''


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

# _BzJ7Rze
# u6#9VXnq
# _3^7EjCU
# b)4SCNLv
# &V4jJIe5
# @d0YDpD$
# )(7nFCg1
# _Ion1BtP
# G&8Jprxr
# $wX3WQjv
# #093Np!@
# +8K5&nSk
# !74YhJ!s
# &U9PZZkr
# Q15(7RUx