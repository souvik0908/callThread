import os
from contextlib import asynccontextmanager
import requests
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from fastapi import FastAPI, Request, Response, status
import asyncio, json, websockets




Base_url = "https://agents.assemblyai.com"


@asynccontextmanager
async def lifespan(app: FastAPI):
    credential = DefaultAzureCredential()

    project_client = AIProjectClient(
        endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        credential=credential,
    )

    openai_client = project_client.get_openai_client()

    app.state.azure_project = project_client
    app.state.openai = openai_client

    yield

    openai_client.close()
    project_client.close()
    credential.close()


app = FastAPI(lifespan=lifespan)



resp = requests.post(
    "https://agents.assemblyai.com/v1/agents",
    headers={"Authorization": os.environ["ASSEMBLYAI_API_KEY"]},
    json={
        "name": "Support Assistant",
        "system_prompt": "You are a friendly support agent. Keep responses under two sentences.",
        "greeting": "Hi, how can I help?",
        "voice": {"voice_id": "alba"},
    },
)
resp.raise_for_status()
print(resp.json())


#{ "id": "7ad24396-b822-4dca-871a-be9cc4781cf9", "name": "Support Assistant", "...": "..." } response structure
agent_id = resp.json()["id"]
@app.get("/get-agents")
def get_agents():
    resp = requests.get(
    "https://agents.assemblyai.com/v1/agents",
    headers={"Authorization": os.environ["ASSEMBLYAI_API_KEY"]},
    )
    resp.raise_for_status()
    return resp.json()

@app.put(f"/update-agent/{agent_id}")
def update_agent(request: Request):
    resp = requests.put(
    f"https://agents.assemblyai.com/v1/agents/{os.environ['AGENT_ID']}",
    headers={"Authorization": os.environ["ASSEMBLYAI_API_KEY"]},
    json={"greeting": "Thanks for calling Acme. What can I do for you?"},
    )
    resp.raise_for_status()
    return resp.json()

    
@app.delete(f"/delete-agent/{agent_id}")
def delete_agent(request: Request):
    resp = requests.delete(
    f"https://agents.assemblyai.com/v1/agents/{os.environ['AGENT_ID']}",
    headers={"Authorization": os.environ["ASSEMBLYAI_API_KEY"]},
    )
    status_code = status.HTTP_204_NO_CONTENT
    return Response(status_code=status_code)


@app.get("/test-agent")
def test_agent(request: Request):
    response = request.app.state.openai.responses.create(
        model=os.environ["AZURE_MODEL_DEPLOYMENT"],
        input="Reply with exactly: CallThread agent is working",
    )
    return {"response": response.output_text}