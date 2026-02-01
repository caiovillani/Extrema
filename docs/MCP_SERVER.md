# MCP Server -- procurement-tools

The procurement MCP server exposes price research and normative
validation tools via the Model Context Protocol (JSON-RPC 2.0 over
stdio).

## Running the Server

```bash
python -m tools.procurement_mcp_server
```

The server is configured in `.mcp.json` for automatic discovery by
Claude Code.

## Available Tools

| Tool | Description |
|------|-------------|
| `validate_source` | Validates whether a normative source is current |
| `search_pncp` | Searches contracts on the National Procurement Portal |
| `get_sinapi_price` | Looks up a SINAPI composition price by code |
| `search_sinapi` | Searches SINAPI compositions by description |
| `get_bps_price` | Queries the Health Price Database |
| `check_cmed_ceiling` | Verifies a price against the CMED ceiling |
| `get_anp_price` | Queries ANP fuel prices by municipality |
| `get_sicro_price` | Looks up a SICRO composition price by code |
| `search_sicro` | Searches SICRO compositions by description |

## Configuration

Environment variables (set in shell or `.env`):

- `SOURCES_LOG` -- Path to normative sources JSONL
- `PRICE_SOURCES_LOG` -- Path to price sources JSONL
- `SINAPI_ESTADO` -- Default state for SINAPI queries (default: MG)
- `SINAPI_CACHE_DIR` -- Local cache for SINAPI data (default: data/sinapi)
- `SICRO_CACHE_DIR` -- Local cache for SICRO data (default: data/sicro)
- `CMED_CACHE_DIR` -- Local cache for CMED data (default: data/cmed)
- `ANP_CACHE_DIR` -- Local cache for ANP data (default: data/anp)
- `AUDIT_LOG` -- Path to audit log JSONL (default: logs/audit.jsonl)

## Audit Logging

All tool invocations are logged to `logs/audit.jsonl` with structured
JSON entries including timestamp, tool name, parameters, duration, and
result summary. This supports audit trail requirements for public
procurement processes.

## Dependencies

```bash
pip install -r requirements.txt
```

Required packages: `mcp`, `httpx`, `openpyxl`.
