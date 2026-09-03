import os
from contextlib import asynccontextmanager

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from fastapi import FastAPI,Request


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

@app.get("/test-agent")
def test_agent(request: Request):
    response = request.app.state.openai.responses.create(
        model=os.environ["AZURE_MODEL_DEPLOYMENT"],
        input="Reply with exactly: CallThread agent is working",
    )
    return {"response": response.output_text}