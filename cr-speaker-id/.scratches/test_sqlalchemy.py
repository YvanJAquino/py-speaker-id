import uuid

import psycopg2
from sqlalchemy import Integer, Column, create_engine, ForeignKey, String, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def guid():
    return str(uuid.uuid4())

Base = declarative_base()


class Account(Base):
    __tablename__ = 'accounts'
    account_id = Column(String, primary_key=True, default=guid)
    account_name = Column(String)
    account_pin = Column(String)


class Phone(Base):
    __tablename__ = 'phones'
    phone_id = Column(String, primary_key=True, default=guid)
    account_id = Column(String, ForeignKey("accounts.account_id"))
    phone_number = Column(String)

    @staticmethod
    def get_account_ids(session, phone_number):
        rows = list(
            session
                .query(Phone.account_id)
                .filter(Phone.phone_number == phone_number)
        )
        return [row[0] for row in rows]


class SpeakerId(Base):
    __tablename__ = 'speakerIds'
    speaker_id = Column(String, primary_key=True, default=guid)
    account_id = Column(String, ForeignKey("accounts.account_id"))
    gcp_resource_name = Column(String)

    @staticmethod
    def get_speaker_ids(session, account_ids):
        rows = list(
            session
                .query(SpeakerId.gcp_resource_name)
                .filter(SpeakerId.account_id.in_(account_ids))
        )
        return [row[0] for row in rows]


def create_tables(engine):
    return Base.metadata.create_all(engine)


if __name__ == '__main__':
    from sqlalchemy import create_engine

    # sudo -u postgres psql
    # CREATE USER speakeridsys WITH ENCRYPTED PASSWORD 'sys';
    # GRANT ALL PRIVILEGES ON DATABASE postgres TO speakeridsys;

    DB_HOST = "localhost"
    DB_PORT = "5432"
    DB_NAME = "postgres"
    DB_USER = "speakeridsys"
    DB_PASS = "sys"

    # dialect+driver://username:password@host:port/database

    DB_CNST = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(DB_CNST, pool_pre_ping=True)
    Session = sessionmaker(engine)
    # create_tables(engine)
    # yvan = Account(account_name="testing", account_pin="4321")
    phone = Phone(account_id="6331fc4c-96d6-4384-927f-22c9520efb1e", phone_number="+17862511624")

    with Session() as session:
        account_ids = Phone.get_account_ids(session, '+17862511624')
        speaker_ids = SpeakerId.get_speaker_ids(session, account_ids)
        print(speaker_ids)
        

