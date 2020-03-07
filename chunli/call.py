from typing import Any, Dict, Optional, TypedDict

from jsondaora import jsondaora


@jsondaora
class Call(TypedDict):
    url: str
    method: Optional[str]
    headers: Optional[Dict[str, str]]
    body: Optional[Dict[str, Any]]
