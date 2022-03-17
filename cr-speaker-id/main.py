import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi import FastAPI

from modules.models import WebhookRequest
from modules.whr_client import WebhookResponse
from modules.sql_models import Account, Phone, SpeakerId

# Reserved for database configuration
DB_HOST = os.environ.get("DB_HOST")
DB_PORT = os.environ.get("DB_PORT")
DB_USER = os.environ.get("DB_USER")
DB_PASS = os.environ.get("DB_PASS")
DB_NAME = os.environ.get("DB_NAME")
DB_CNST = os.environ.get("DB_CNST") # DB_CNST = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Database engine and session objects
engine = create_engine(DB_CNST)
Session = sessionmaker(engine)

app = FastAPI()

@app.post("/get-speaker-ids")
async def get_speaker_ids(webhook: WebhookRequest):
    response = WebhookResponse()
    phone = webhook.payload['telephony']['caller_id']
    with Session() as session:
        account_ids = Phone.get_account_ids(session, phone)
        if not account_ids:
            response.add_text_response(f"AccountError: No account was found for {phone}.")
            return response.to_dict()
        speaker_ids = SpeakerId.get_speaker_ids(session, account_ids)
        if not speaker_ids:
            response.add_text_response("SpeakerIderror: No speakerIds were found.")
            return response.to_dict()
        else:
            response.add_text_response("SpeakerIds found!  Let's move on...")
            response = response.to_dict()
            session_params = {'sessionInfo': {
                'parameters': {
                    'speaker-ids': speaker_ids
                    }
                }
            }
            response.update(session_params)
            return response

@app.post("/register-speaker-ids")
async def register_speaker_ids(webhook: WebhookRequest):
    response = WebhookResponse()
    phone = webhook.payload['telephony']['caller_id']
    new_speaker_id = webhook.sessionInfo.parameters['new-speaker-id']
    with Session() as session:
        account_ids = Phone.get_account_ids(session, phone)
        if not account_ids:
            response.add_text_response(f"AccountError: No account was found for {phone}.")
            return response.to_dict()
        account_id = account_ids[0]
        session.add(SpeakerId(gcp_resource_name=new_speaker_id, account_id=account_id))
        response.add_text_response("A new speaker ID has been registered.")
        response = response.to_dict()
        session_params = {'sessionInfo': {
            'parameters': {
                'speakerIdRegistered': True,
                'userAuthenticated': True
                }
            }
        }
        response.update(session_params)
        return response

@app.post("verify-pin")
async def verify_pin(webhook: WebhookRequest):
    response = WebhookResponse()
    phone = webhook.payload['telephony']['caller_id']
    pin = webhook.pageInfo['formInfo']['parameterInfo'][0]['value']
    with Session() as session:
        account_ids = Phone.get_account_ids(session, phone)
        if not account_ids:
            response.add_text_response(f"AccountError: No account was found for {phone}.")
            return response.to_dict()
        pins = Account.get_pins(session, account_ids)
        response.add_text_response("Your authenticated and very beautiful.")
        response = response.to_dict()
        session_params = {'sessionInfo': {
            'parameters': {
                'userAuthenticated': pin in pins
                }
            }
        }
        response.update(session_params)
        return response


