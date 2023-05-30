from sqlalchemy import Column, String, Integer

from app import db

class Credential(db.Model):
    __tablename__ = 'credential'
    id = Column(String(64), primary_key=True)
    name = Column(String(), nullable=False)
    url = Column(String(), nullable=True)
    provider = Column(String(), nullable=True)
    type = Column(String(32), nullable=False)
    description = Column(String(), nullable=True)
    eligibility_education = Column(String(32), nullable=True)
    eligibility_experience = Column(String(8), nullable=True)
    eligibility_training = Column(String(8), nullable=True)

    def __str__(self):
        return self.name


class Program(db.Model):
    __tablename__ = 'program'
    id = Column(String(64), primary_key=True)
    name = Column(String())
    url = Column(String())
    provider = Column(String())
    credential_uuid = Column(String(64))
    delivery_method = Column(String(32))
    duration = Column(String(4))
    price = Column(String(8))
    location = Column(String())

    def __str__(self):
        return self.name
    

class JobRole(db.Model):
    __tablename__ = 'job_role'
    id = Column(String(64), primary_key=True)
    name = Column(String())
    onet_code = Column(String())
    url = Column(String())

    def __str__(self):
        return self.name
    

class CredentialJobRole(db.Model):
    __tablename__ = 'credential_job_role'
    index = Column(Integer(), primary_key=True)
    credential_uuid = Column(String(64))
    job_role_id = Column(String())

    def __str__(self):
        return self.credential_uuid + ' | ' + self.job_role_id