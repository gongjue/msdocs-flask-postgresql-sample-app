import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
# from jinja2 import Environment

app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# def provider_format(value):
#     value_1 = value.replace("-", " - ")
#     tokens = value_1.split(" ")
#     skip_words = ["of", "in", "for"]
#     tokens_cap = [s.capitalize() for s in tokens if s not in skip_words]
#     return " ".join(tokens_cap).replace(" - ", "-")

# env = Environment()
# env.filters['provider_format'] = provider_format

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import Credential, Program, JobRole, CredentialJobRole

@app.route('/', methods=['GET'])
def index():
    print('Request for index page received')
    credentials = Credential.query.all()
    return render_template('index.html', credentials=credentials)

@app.route('/credential/<string:id>', methods=['GET'])
def credential_details(id):
    credential = Credential.query.where(Credential.id == id).first()
    programs = Program.query.where(Program.credential_uuid == id)
    job_roles = JobRole.query.join(
        CredentialJobRole, JobRole.id == CredentialJobRole.job_role_id).where(
        CredentialJobRole.credential_uuid == id)
    # programs = None
    print(programs.count())
    return render_template('credential_details.html',
                           credential=credential,
                           programs=programs,
                           job_roles=job_roles)

@app.route('/program/<string:id>', methods=['GET'])
def program_details(id):
    program = Program.query.where(Program.id == id).first()
    return render_template('program_details.html', program=program)

@app.route('/job_role/<string:id>', methods=['GET'])
def job_role_details(id):
    job_role = JobRole.query.where(JobRole.id == id).first()
    credentials = Credential.query.join(
        CredentialJobRole, Credential.id == CredentialJobRole.credential_uuid).where(
        CredentialJobRole.job_role_id == id)
    return render_template('job_role_details.html', job_role=job_role, credentials=credentials)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/api/credential', methods=['GET'])
def data():
    query = Credential.query

    # search filter
    search = request.args.get('search[value]')
    if search:
        query = query.filter(db.or_(
            Credential.credential_name.like(f'%{search}%'),
        ))
    total_filtered = query.count()

    # sorting
    order = []
    i = 0
    while True:
        col_index = request.args.get(f'order[{i}][column]')
        if col_index is None:
            break
        col_name = request.args.get(f'columns[{col_index}][data]')
        if col_name not in ['credential_name', 'credential_type']:
            col_name = 'credential_name'
        descending = request.args.get(f'order[{i}][dir]') == 'desc'
        col = getattr(Credential, col_name)
        if descending:
            col = col.desc()
        order.append(col)
        i += 1
    if order:
        query = query.order_by(*order)

    # pagination
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    query = query.offset(start).limit(length)

    # response
    return {
        'data': [credential.to_dict() for credential in query],
        'recordsFiltered': total_filtered,
        'recordsTotal': Credential.query.count(),
        'draw': request.args.get('draw', type=int),
    }


if __name__ == '__main__':
    app.run()
