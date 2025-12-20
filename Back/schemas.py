from pydantic import BaseModel

class EchoRequest(BaseModel):
    message: str

#DB저장 테스트 요청용 pydantic
class ItemRequest(BaseModel):
    content: str

#DB저장 테스트 응답용 pydantic
class ItemResponse(BaseModel):
    id: int
    content: str

