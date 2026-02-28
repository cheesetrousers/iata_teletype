import os
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import pubsub_v1
from .builder import IataMessageBuilder

# Force use of emulator for Google Cloud SDK
os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8085"

PROJECT_ID = "iata-teletype-project"
TOPIC_ID = "teletype-messages"

class TeletypePayload(BaseModel):
    destination: str
    origin: str
    tag: Optional[str] = None
    body: str
    ordering_key: Optional[str] = None

publish_client = None
topic_path = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global publish_client, topic_path
    
    # Enable ordering capabilities
    publisher_options = pubsub_v1.types.PublisherOptions(enable_message_ordering=True)
    publish_client = pubsub_v1.PublisherClient(publisher_options=publisher_options)
    topic_path = publish_client.topic_path(PROJECT_ID, TOPIC_ID)
    
    # Try explicitly creating to ensure topic exists in the mock environment
    try:
        publish_client.create_topic(request={"name": topic_path})
        print(f"Created Topic: {topic_path} on Emulator.")
    except Exception as e:
        print(f"Assuming topic already exists or could not create: {e}")

    yield

    if publish_client:
        print("Shutting down pubsub client...")

app = FastAPI(lifespan=lifespan, title="IATA Teletype API")

@app.post("/messages/teletype")
async def publish_teletype(payload: TeletypePayload):
    try:
        # Determine the ordering key (default to destination)
        ord_key = payload.ordering_key if payload.ordering_key else payload.destination
        
        # Build the teletype ASCII string
        ascii_msg = IataMessageBuilder.build(
            payload.destination,
            payload.origin,
            payload.body,
            payload.tag
        )
        
        # Publish the message with ordering key
        future = publish_client.publish(
            topic_path,
            data=ascii_msg.encode("utf-8"),
            ordering_key=ord_key
        )
        message_id = future.result()
        
        return {"status": "success", "message_id": message_id, "ordering_key": ord_key}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def run():
    import uvicorn
    uvicorn.run("message_builder.api:app", host="0.0.0.0", port=8000, reload=True)

if __name__ == "__main__":
    run()
