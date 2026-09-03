import json
import re
from collections.abc import Callable

from langchain.agents.middleware import AgentMiddleware, wrap_tool_call
from langchain.messages import ToolMessage
from langchain.tools.tool_node import ToolCallRequest


def is_valid_cpf(cpf: str) -> bool:
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for i in (9, 10):
        total = sum(int(cpf[num]) * (i + 1 - num) for num in range(i))
        digit = (total * 10 % 11) % 10
        if digit != int(cpf[i]):
            return False
    return True


def detect_cpf(content: str) -> list[dict]:
    matches = []
    for match in re.finditer(r"\d{3}\.\d{3}\.\d{3}-\d{2}", content):
        cpf = re.sub(r"\D", "", match.group(0))
        if is_valid_cpf(cpf):
            matches.append({"text": match.group(0), "start": match.start(), "end": match.end()})
    return matches


class PatientAccessGuardrail(AgentMiddleware):
    def wrap_tool_call(self, request: ToolCallRequest, handler) -> ToolMessage:
        # # TODO: pegue o patient_id pedido nos args da tool e o patient_id da conversa atual
        # requested_id = ...
        # current_id = ...
        # if request.tool_call["name"] == "get_patient_record" and requested_id and requested_id != current_id:
        #     # TODO: monte o payload de bloqueio (status, reason, message)
        #     payload = ...
        #     return ToolMessage(content=json.dumps(payload), tool_call_id=request.tool_call["id"])
        # return handler(request)
        raise NotImplementedError


@wrap_tool_call
def retry_tool(request: ToolCallRequest, handler: Callable) -> ToolMessage:
    for attempt in range(3):
        try:
            return handler(request)
        except Exception:
            if attempt == 2:
                raise


def needs_approval(request: ToolCallRequest) -> bool:
    specialty = request.tool_call["args"].get("specialty", "")
    return specialty.lower() == "cardiologia"


APPROVAL_POLICY = {
    "book_appointment": {
        "description": "Agendamento de cardiologia precisa de aprovação antes de confirmar.",
        "allowed_decisions": ["approve", "reject"],
        "when": needs_approval,
    }
}
