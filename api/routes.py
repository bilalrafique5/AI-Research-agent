from fastapi import APIRouter
from services.workflow import run_workflow

router=APIRouter()

@router.post("/research")
async def research(query: str):
    result=await run_workflow(query)
    return {"result":result}
    
    
    