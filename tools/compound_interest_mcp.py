"""Expose the compound-interest calculator as a stdio MCP server."""

import json
import math
import sys
from typing import Any

from compound_interest import calculate_compound_interest


PROTOCOL_VERSION = "2025-03-26"
SUPPORTED_PROTOCOL_VERSIONS = (PROTOCOL_VERSION, "2024-11-05")
TOOL = {
    "name": "calculate_compound_interest",
    "description": (
        "Calculate the final amount and interest earned using periodic "
        "compound interest."
    ),
    "inputSchema": {
        "type": "object",
        "properties": {
            "principal": {
                "type": "number",
                "minimum": 0,
                "description": "Initial amount of money.",
            },
            "annual_rate": {
                "type": "number",
                "minimum": 0,
                "description": (
                    "Annual interest rate as a percentage; use 7.34 for 7.34%."
                ),
            },
            "compounds_per_year": {
                "type": "integer",
                "minimum": 1,
                "description": "Number of compounding periods per year.",
            },
            "years": {
                "type": "number",
                "minimum": 0,
                "description": "Total investment duration in years.",
            },
        },
        "required": [
            "principal",
            "annual_rate",
            "compounds_per_year",
            "years",
        ],
        "additionalProperties": False,
    },
}


def write_message(message: dict[str, Any]) -> None:
    sys.stdout.write(json.dumps(message, separators=(",", ":"), allow_nan=False))
    sys.stdout.write("\n")
    sys.stdout.flush()


def write_error(request_id: Any, code: int, message: str) -> None:
    write_message(
        {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": code, "message": message},
        }
    )


def calculate(arguments: Any) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a JSON object.")

    required = ("principal", "annual_rate", "compounds_per_year", "years")
    missing = [name for name in required if name not in arguments]
    if missing:
        raise ValueError(f"Missing required argument(s): {', '.join(missing)}.")
    extra = set(arguments) - set(required)
    if extra:
        raise ValueError(f"Unexpected argument(s): {', '.join(sorted(extra))}.")

    principal = arguments["principal"]
    annual_rate = arguments["annual_rate"]
    compounds_per_year = arguments["compounds_per_year"]
    years = arguments["years"]
    numeric_values: dict[str, float] = {}
    for name, value in (
        ("principal", principal),
        ("annual_rate", annual_rate),
        ("years", years),
    ):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError(f"{name} must be a number.")
        try:
            numeric_value = float(value)
        except OverflowError:
            raise ValueError(f"{name} exceeds the supported numeric range.") from None
        if not math.isfinite(numeric_value) or numeric_value < 0:
            raise ValueError(f"{name} must be finite and non-negative.")
        numeric_values[name] = numeric_value
    if isinstance(compounds_per_year, bool) or not isinstance(
        compounds_per_year, int
    ):
        raise ValueError("compounds_per_year must be a positive integer.")
    if compounds_per_year <= 0:
        raise ValueError("compounds_per_year must be a positive integer.")

    try:
        final_amount, interest_earned = calculate_compound_interest(
            numeric_values["principal"],
            numeric_values["annual_rate"],
            compounds_per_year,
            numeric_values["years"],
        )
    except OverflowError:
        raise ValueError(
            "The supplied values exceed the supported calculation range."
        ) from None
    if not math.isfinite(final_amount) or not math.isfinite(interest_earned):
        raise ValueError("The supplied values exceed the supported calculation range.")

    return {
        "final_amount": final_amount,
        "interest_earned": interest_earned,
    }


def handle_request(request: Any) -> dict[str, Any] | None:
    if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id") if isinstance(request, dict) else None,
            "error": {"code": -32600, "message": "Invalid Request"},
        }

    method = request.get("method")
    request_id = request.get("id")
    if "id" not in request:
        return None

    if method == "initialize":
        params = request.get("params")
        requested_version = (
            params.get("protocolVersion") if isinstance(params, dict) else None
        )
        protocol_version = (
            requested_version
            if requested_version in SUPPORTED_PROTOCOL_VERSIONS
            else PROTOCOL_VERSION
        )
        result = {
            "protocolVersion": protocol_version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": "compound-interest", "version": "1.0.0"},
        }
    elif method == "ping":
        result = {}
    elif method == "tools/list":
        result = {"tools": [TOOL]}
    elif method == "tools/call":
        params = request.get("params")
        if not isinstance(params, dict):
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "Invalid tool parameters."},
            }
        if params.get("name") != TOOL["name"]:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32602, "message": "Unknown tool."},
            }
        try:
            calculation = calculate(params.get("arguments"))
        except ValueError as error:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "content": [{"type": "text", "text": str(error)}],
                    "isError": True,
                },
            }
        final_amount = calculation["final_amount"]
        interest_earned = calculation["interest_earned"]
        result = {
            "content": [
                {
                    "type": "text",
                    "text": (
                        f"Final amount: ${final_amount:,.2f}\n"
                        f"Interest earned: ${interest_earned:,.2f}"
                    ),
                }
            ],
            "structuredContent": calculation,
            "isError": False,
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": "Method not found"},
        }

    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main() -> int:
    for line in sys.stdin:
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            write_error(None, -32700, "Parse error")
            continue
        try:
            response = handle_request(request)
        except (TypeError, ValueError):
            write_error(
                request.get("id") if isinstance(request, dict) else None,
                -32603,
                "Internal error",
            )
            continue
        if response is not None:
            write_message(response)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
