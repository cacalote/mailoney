from datetime import datetime

from sqlalchemy import *
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

Base = declarative_base()

# Credentials Table

class SMTPCredentials(Base):
    __tablename__ = 'smtp_credentials'

    id = Column(Integer(), primary_key=True)
    connection_time = Column(DateTime(timezone=False), default=datetime.now(), nullable=False)
    remote_ip = Column(String(255), nullable=True)
    smtp_user = Column(String(255), nullable=True)
    smtp_pass = Column(String(255), nullable=True)

    def __init__(self, remote_ip, smtp_user, smtp_pass):
        self.remote_ip = remote_ip
        self.smtp_user = smtp_user
        self.smtp_pass = smtp_pass

    def __repr__(self):
        return {'id':self.id,
                'smtp_user':self.smtp_user,
                'smtp_pass':self.smtp_pass
                }

class SMTPEmails(Base):
    __tablename__ = 'smtp_emails'

    id = Column(Integer(), primary_key=True)
    connection_time = Column(DateTime(timezone=False), default=datetime.now(), nullable=False)
    remote_ip = Column(String(255), nullable=True)
    email_to = Column(String(255), nullable=True)
    email_from = Column(String(255), nullable=True)
    email_data = Column(Text(), nullable=True)

    def __init__(self, remote_ip, email_to, email_from, email_data):
        self.remote_ip = remote_ip
        self.email_to = email_to
        self.email_from = email_from
        self.email_data = email_data

    def __repr__(self):
        return {'id':self.id,
                'remote_ip':self.remote_ip,
                'email_to':self.email_to,
                'email_from':self.email_from,
                'email_data':self.email_data
                }


class Database:

    def __init__(self):
        self.engine = create_engine('sqlite:///mailoney.db', poolclass=NullPool)

        self.engine.echo = False
        self.engine.pool_timeout = 60

        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def __del__(self):
        self.engine.dispose()

    def add_creds(self, remote_ip, smtp_user, smtp_pass):
        session = self.Session()
        try:
            creds = SMTPCredentials(remote_ip, smtp_user, smtp_pass)
            session.add(creds)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False

    def add_email(self, remote_ip, email_to, email_from, email_data):
        session = self.Session()
        try:
            email = SMTPEmails(remote_ip, email_to, email_from, email_data)
            session.add(email)
            session.commit()
            return True
        except IntegrityError:
            session.rollback()
            return False