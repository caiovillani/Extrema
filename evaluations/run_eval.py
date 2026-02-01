"""
Evaluation runner for procurement system skills.

Validates that the core infrastructure works:
- Source log loading
- Client instantiation
- Tool method execution (validation, search)
- Hook scripts execution

Usage:
    python -m evaluations.run_eval
"""

import asyncio
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

# Ensure project root is on the path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
os.chdir(PROJECT_ROOT)

PASS = "PASS"
FAIL = "FAIL"
SKIP = "SKIP"


def result_line(test_id: str, status: str, detail: str = ""):
    tag = {"PASS": "+", "FAIL": "!", "SKIP": "~"}[status]
    msg = f"  [{tag}] {test_id}"
    if detail:
        msg += f" -- {detail}"
    print(msg)
    return status


async def test_source_loading():
    """Test that ProcurementTools loads sources correctly."""
    from tools.procurement_mcp_server import ProcurementTools

    tools = ProcurementTools()
    results = []

    # T1: sources loaded
    n = len(tools.sources)
    if n > 0:
        results.append(result_line(
            "T1-sources-loaded", PASS,
            f"{n} normative sources",
        ))
    else:
        results.append(result_line(
            "T1-sources-loaded", FAIL,
            "no sources loaded",
        ))

    # T2: price sources loaded
    n = len(tools.price_sources)
    if n > 0:
        results.append(result_line(
            "T2-price-sources-loaded", PASS,
            f"{n} price sources",
        ))
    else:
        results.append(result_line(
            "T2-price-sources-loaded", FAIL,
            "no price sources loaded",
        ))

    # T3: validate a known-good source
    r = tools.validate_source("BR-FED-0001")
    if r.get("valid"):
        results.append(result_line(
            "T3-validate-known-source", PASS,
        ))
    else:
        results.append(result_line(
            "T3-validate-known-source", FAIL,
            str(r),
        ))

    # T4: validate a bad source
    r = tools.validate_source("NONEXISTENT")
    if not r.get("valid"):
        results.append(result_line(
            "T4-validate-bad-source", PASS,
        ))
    else:
        results.append(result_line(
            "T4-validate-bad-source", FAIL,
            "should have been invalid",
        ))

    await tools.close()
    return results


async def test_pncp_client():
    """Test PNCP client instantiation and search."""
    from tools.pncp_client import PNCPClient
    from tools.http_utils import CachedHTTPClient

    http = CachedHTTPClient()
    client = PNCPClient(http=http)
    results = []

    # T5: search returns PNCPSearchResult
    r = await client.search_contratos("computador", uf="MG", limite=3)
    if hasattr(r, "termo") and r.termo == "computador":
        results.append(result_line(
            "T5-pncp-search-structure", PASS,
            f"total={r.total_resultados}",
        ))
    else:
        results.append(result_line(
            "T5-pncp-search-structure", FAIL,
        ))

    await http.close()
    return results


async def test_sinapi_client():
    """Test SINAPI client CSV parsing."""
    from tools.sinapi_client import SINAPIClient
    from tools.http_utils import CachedHTTPClient
    import tempfile
    import csv

    results = []

    # Create a test CSV
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False,
        encoding="latin-1",
    ) as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "CODIGO", "DESCRICAO", "UNIDADE", "PRECO UNITARIO"
        ])
        writer.writerow([
            "87529", "PINTURA LATEX PVA", "M2", "12,50"
        ])
        writer.writerow([
            "87878", "PISO CERAMICO", "M2", "45,30"
        ])
        writer.writerow([
            "93358", "ELETRODUTO PVC", "M", "8,75"
        ])
        tmp_path = f.name

    http = CachedHTTPClient()
    client = SINAPIClient(estado="MG", http=http)
    client.load_from_csv(tmp_path)

    # T6: CSV loaded correctly
    comp = client.get_composicao("87529")
    if comp and comp.preco_unitario == 12.50:
        results.append(result_line(
            "T6-sinapi-csv-load", PASS,
            f"code=87529 price={comp.preco_unitario}",
        ))
    else:
        results.append(result_line(
            "T6-sinapi-csv-load", FAIL,
            f"comp={comp}",
        ))

    # T7: search by description
    found = client.search_composicoes("PISO")
    if len(found) == 1 and found[0].codigo == "87878":
        results.append(result_line(
            "T7-sinapi-search", PASS,
        ))
    else:
        results.append(result_line(
            "T7-sinapi-search", FAIL,
            f"found={len(found)}",
        ))

    # T8: BDI calculation
    bdi_result = client.calcular_composicao_com_bdi(
        [("87529", 200), ("87878", 200)], bdi=22.12
    )
    expected_sub = round(12.50 * 200 + 45.30 * 200, 2)
    if bdi_result["subtotal"] == expected_sub:
        results.append(result_line(
            "T8-sinapi-bdi-calc", PASS,
            f"subtotal={expected_sub} total={bdi_result['total']}",
        ))
    else:
        results.append(result_line(
            "T8-sinapi-bdi-calc", FAIL,
            f"expected {expected_sub}, got {bdi_result['subtotal']}",
        ))

    os.unlink(tmp_path)
    await http.close()
    return results


async def test_bps_client():
    """Test BPS client CSV parsing and CMED verification."""
    from tools.bps_client import BPSClient, CMEDPreco
    from tools.http_utils import CachedHTTPClient
    import tempfile
    import csv

    results = []
    http = CachedHTTPClient()
    client = BPSClient(http=http)

    # Create test BPS CSV
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False,
        encoding="utf-8",
    ) as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "MEDICAMENTO", "APRESENTACAO", "PRINCIPIO_ATIVO",
            "PRECO_UNITARIO", "ORGAO", "UF", "DATA_COMPRA",
            "QUANTIDADE", "MODALIDADE",
        ])
        writer.writerow([
            "RISPERIDONA 2MG", "COMPRIMIDO", "RISPERIDONA",
            "0,15", "PREF EXEMPLO", "MG", "2025-06-15",
            "5000", "PREGAO",
        ])
        writer.writerow([
            "RISPERIDONA 2MG", "COMPRIMIDO", "RISPERIDONA",
            "0,18", "SEC SAUDE", "SP", "2025-07-10",
            "10000", "PREGAO",
        ])
        writer.writerow([
            "RISPERIDONA 2MG", "COMPRIMIDO", "RISPERIDONA",
            "0,12", "HOSPITAL X", "MG", "2025-08-01",
            "3000", "PREGAO",
        ])
        bps_path = f.name

    client.load_bps_csv(bps_path)

    # T9: BPS search returns summary
    resumo = client.search_bps("RISPERIDONA")
    if resumo and resumo.n_registros == 3:
        results.append(result_line(
            "T9-bps-search", PASS,
            f"n={resumo.n_registros} media={resumo.media}",
        ))
    else:
        results.append(result_line(
            "T9-bps-search", FAIL,
            f"resumo={resumo}",
        ))

    # T10: BPS search with UF filter
    resumo_mg = client.search_bps("RISPERIDONA", uf="MG")
    if resumo_mg and resumo_mg.n_registros == 2:
        results.append(result_line(
            "T10-bps-filter-uf", PASS,
            f"MG records={resumo_mg.n_registros}",
        ))
    else:
        results.append(result_line(
            "T10-bps-filter-uf", FAIL,
            f"expected 2, got {resumo_mg}",
        ))

    # T11: CMED teto verification (mock data)
    client._cmed_data["RISPERIDONA|COMPRIMIDO"] = CMEDPreco(
        medicamento="RISPERIDONA",
        apresentacao="COMPRIMIDO",
        laboratorio="LAB",
        pf_sem_impostos=0.25,
        pmvg_sem_impostos=0.20,
        pmvg_com_impostos=0.22,
        lista_concessao="POSITIVA",
        data_publicacao="2025-12-01",
    )
    client._cmed_loaded = True

    check = client.verificar_teto("RISPERIDONA", 0.15, "COMPRIMIDO")
    if check.get("verificado") and check.get("dentro_do_teto"):
        results.append(result_line(
            "T11-cmed-within-ceiling", PASS,
        ))
    else:
        results.append(result_line(
            "T11-cmed-within-ceiling", FAIL,
            str(check),
        ))

    check2 = client.verificar_teto("RISPERIDONA", 0.25, "COMPRIMIDO")
    if check2.get("verificado") and not check2.get("dentro_do_teto"):
        results.append(result_line(
            "T12-cmed-above-ceiling", PASS,
        ))
    else:
        results.append(result_line(
            "T12-cmed-above-ceiling", FAIL,
            str(check2),
        ))

    os.unlink(bps_path)
    await http.close()
    return results


def test_hook_validate_document():
    """Test the validate_document hook script."""
    results = []
    hook = PROJECT_ROOT / ".claude" / "hooks" / "validate_document.py"

    # T13: Valid ETP passes
    etp_content = """
## 1. Descricao da Necessidade
Teste

## 2. Requisitos da Contratacao
Teste

## 3. Estimativa de Quantidades e Valor
R$ 1.000,00

## 4. Justificativa da Solucao
Teste

[Fonte: BR-FED-0001 | Lei 14.133/2021 | Art. 18 | Vigente]
"""
    r = subprocess.run(
        [sys.executable, str(hook), "--type", "etp"],
        input=etp_content, capture_output=True, text=True,
    )
    if r.returncode == 0:
        results.append(result_line("T13-hook-valid-etp", PASS))
    else:
        results.append(result_line(
            "T13-hook-valid-etp", FAIL, r.stdout + r.stderr,
        ))

    # T14: Invalid ETP (missing sections) fails
    bad_etp = "# Some random content\nNo sections here.\n"
    r = subprocess.run(
        [sys.executable, str(hook), "--type", "etp"],
        input=bad_etp, capture_output=True, text=True,
    )
    if r.returncode != 0:
        results.append(result_line("T14-hook-invalid-etp", PASS))
    else:
        results.append(result_line(
            "T14-hook-invalid-etp", FAIL,
            "should have failed",
        ))

    return results


def test_hook_check_citation():
    """Test the check_citation hook script."""
    results = []
    hook = PROJECT_ROOT / ".claude" / "hooks" / "check_citation.py"

    # Create temp file with valid citations
    import tempfile
    content = (
        "Conforme o Art. 18 da Lei 14.133/2021\n"
        "[Fonte: BR-FED-0001 | Lei 14.133/2021 | Art. 18 | Vigente]\n"
    )
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".md", delete=False,
    ) as f:
        f.write(content)
        tmp = f.name

    r = subprocess.run(
        [sys.executable, str(hook), "--file", tmp],
        capture_output=True, text=True,
        env={
            **os.environ,
            "SOURCES_LOG": str(
                PROJECT_ROOT / "sources" / "sources_log.jsonl"
            ),
            "PRICE_SOURCES_LOG": str(
                PROJECT_ROOT / "sources" / "price_sources_log.jsonl"
            ),
        },
    )
    if r.returncode == 0:
        results.append(result_line(
            "T15-hook-citation-valid", PASS,
        ))
    else:
        results.append(result_line(
            "T15-hook-citation-valid", FAIL,
            r.stdout + r.stderr,
        ))

    os.unlink(tmp)
    return results


def test_http_utils():
    """Test HTTP utilities (cache, credentials)."""
    from tools.http_utils import TTLCache, load_credentials

    results = []

    # T16: TTL cache works
    cache = TTLCache(default_ttl=60)
    cache.set("http://example.com", {"data": 1})
    val = cache.get("http://example.com")
    if val == {"data": 1}:
        results.append(result_line("T16-cache-hit", PASS))
    else:
        results.append(result_line("T16-cache-hit", FAIL))

    # T17: Cache miss for unknown URL
    val = cache.get("http://unknown.com")
    if val is None:
        results.append(result_line("T17-cache-miss", PASS))
    else:
        results.append(result_line("T17-cache-miss", FAIL))

    # T18: Credentials load without error
    try:
        creds = load_credentials()
        results.append(result_line(
            "T18-credentials-load", PASS,
            f"{len(creds)} keys",
        ))
    except Exception as exc:
        results.append(result_line(
            "T18-credentials-load", FAIL, str(exc),
        ))

    return results


async def test_anp_client():
    """Test ANP client CSV parsing and search."""
    from tools.anp_client import ANPClient
    from tools.http_utils import CachedHTTPClient
    import tempfile

    results = []

    # Create test CSV with ANP-style data
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False,
        encoding="latin-1",
    ) as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "COMBUSTIVEL", "MUNICIPIO", "ESTADO",
            "PRECO_REVENDA", "BANDEIRA", "DATA_COLETA",
            "NOME_POSTO",
        ])
        writer.writerow([
            "GASOLINA COMUM", "EXTREMA", "MG",
            "5,89", "BRANCA", "2026-01-25", "POSTO A",
        ])
        writer.writerow([
            "GASOLINA COMUM", "EXTREMA", "MG",
            "5,95", "SHELL", "2026-01-25", "POSTO B",
        ])
        writer.writerow([
            "DIESEL S10", "EXTREMA", "MG",
            "6,15", "BRANCA", "2026-01-25", "POSTO C",
        ])
        tmp_path = f.name

    http = CachedHTTPClient()
    client = ANPClient(
        municipio="EXTREMA", estado="MG", http=http,
    )
    client.load_from_csv(tmp_path)

    # T19: CSV loaded correctly
    if client._loaded and len(client._registros) == 3:
        results.append(result_line(
            "T19-anp-csv-load", PASS,
            f"records={len(client._registros)}",
        ))
    else:
        results.append(result_line(
            "T19-anp-csv-load", FAIL,
        ))

    # T20: search returns results
    postos = client.search_postos(
        "GASOLINA COMUM", "EXTREMA",
    )
    if len(postos) == 2:
        results.append(result_line(
            "T20-anp-search", PASS,
        ))
    else:
        results.append(result_line(
            "T20-anp-search", FAIL,
            f"found={len(postos)}",
        ))

    # T21: price summary structure
    resumo = client.get_precos("GASOLINA COMUM", "EXTREMA")
    if (
        resumo
        and resumo.n_postos == 2
        and resumo.media > 0
    ):
        results.append(result_line(
            "T21-anp-price-summary", PASS,
            f"media={resumo.media}",
        ))
    else:
        results.append(result_line(
            "T21-anp-price-summary", FAIL,
        ))

    os.unlink(tmp_path)
    await http.close()
    return results


async def test_sicro_client():
    """Test SICRO client CSV parsing and search."""
    from tools.sicro_client import SICROClient
    from tools.http_utils import CachedHTTPClient
    import tempfile

    results = []

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False,
        encoding="latin-1",
    ) as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow([
            "CODIGO", "DESCRICAO", "UNIDADE",
            "PRECO UNITARIO",
        ])
        writer.writerow([
            "5914242", "ESCAVACAO MECANICA", "M3", "8,45",
        ])
        writer.writerow([
            "4011631", "TRANSPORTE LOCAL MATERIAL",
            "TKM", "1,20",
        ])
        writer.writerow([
            "5914315", "COMPACTACAO DE ATERRO",
            "M3", "5,60",
        ])
        tmp_path = f.name

    http = CachedHTTPClient()
    client = SICROClient(estado="MG", http=http)
    client.load_from_csv(tmp_path)

    # T22: CSV loaded
    comp = client.get_composicao("5914242")
    if comp and comp.preco_unitario == 8.45:
        results.append(result_line(
            "T22-sicro-csv-load", PASS,
            f"code=5914242 price={comp.preco_unitario}",
        ))
    else:
        results.append(result_line(
            "T22-sicro-csv-load", FAIL,
        ))

    # T23: search by description
    found = client.search_composicoes("COMPACTACAO")
    if len(found) == 1 and found[0].codigo == "5914315":
        results.append(result_line(
            "T23-sicro-search", PASS,
        ))
    else:
        results.append(result_line(
            "T23-sicro-search", FAIL,
            f"found={len(found)}",
        ))

    # T24: composition structure
    comp2 = client.get_composicao("4011631")
    if (
        comp2
        and comp2.unidade == "TKM"
        and comp2.estado == "MG"
    ):
        results.append(result_line(
            "T24-sicro-structure", PASS,
        ))
    else:
        results.append(result_line(
            "T24-sicro-structure", FAIL,
        ))

    os.unlink(tmp_path)
    await http.close()
    return results


async def test_e2e_workflows():
    """End-to-end workflow tests."""
    from tools.procurement_mcp_server import ProcurementTools
    from tools.sinapi_client import SINAPIClient
    from tools.sicro_client import SICROClient
    from tools.anp_client import ANPClient

    results = []
    tools = ProcurementTools()

    # T25: Multi-source clients are all instantiated
    has_sinapi = isinstance(tools.sinapi, SINAPIClient)
    has_sicro = isinstance(tools.sicro, SICROClient)
    has_anp = isinstance(tools.anp, ANPClient)
    if has_sinapi and has_sicro and has_anp:
        results.append(result_line(
            "T25-multi-source-clients", PASS,
        ))
    else:
        results.append(result_line(
            "T25-multi-source-clients", FAIL,
            f"sinapi={has_sinapi} sicro={has_sicro} "
            f"anp={has_anp}",
        ))

    # T26: Source + citation round-trip
    r = tools.validate_source("BR-FED-0001")
    if r.get("valid") and r.get("source", {}).get("nome"):
        source = r["source"]
        citation = (
            f"[Fonte: {source['id']} | {source['nome']} "
            f"| Art. 23 | "
            f"{source['status'].capitalize()}]"
        )
        if (
            "BR-FED-0001" in citation
            and "Lei 14.133" in citation
        ):
            results.append(result_line(
                "T26-citation-round-trip", PASS,
            ))
        else:
            results.append(result_line(
                "T26-citation-round-trip", FAIL,
                citation,
            ))
    else:
        results.append(result_line(
            "T26-citation-round-trip", FAIL, str(r),
        ))

    # T27: Audit logging works
    from tools.logging_config import audit_log, AUDIT_LOG_PATH
    import tempfile
    import json as _json

    # Use a temp file to avoid polluting real logs
    old_path = AUDIT_LOG_PATH
    tmp = tempfile.NamedTemporaryFile(
        suffix=".jsonl", delete=False,
    )
    tmp.close()
    import tools.logging_config as lc
    lc.AUDIT_LOG_PATH = Path(tmp.name)

    audit_log(
        "test_tool", {"key": "val"}, {"success": True}, 1.5,
    )

    content = Path(tmp.name).read_text()
    lc.AUDIT_LOG_PATH = old_path
    os.unlink(tmp.name)

    try:
        entry = _json.loads(content.strip())
        if (
            entry.get("tool") == "test_tool"
            and entry.get("duration_ms") == 1.5
        ):
            results.append(result_line(
                "T27-audit-logging", PASS,
            ))
        else:
            results.append(result_line(
                "T27-audit-logging", FAIL, str(entry),
            ))
    except Exception as exc:
        results.append(result_line(
            "T27-audit-logging", FAIL, str(exc),
        ))

    await tools.close()
    return results


async def main():
    print("=" * 60)
    print("Procurement System -- Evaluation Runner")
    print("=" * 60)
    print()

    all_results = []

    print("[1] Source loading and validation")
    all_results.extend(await test_source_loading())
    print()

    print("[2] PNCP client")
    all_results.extend(await test_pncp_client())
    print()

    print("[3] SINAPI client (CSV parsing + BDI)")
    all_results.extend(await test_sinapi_client())
    print()

    print("[4] BPS/CMED client (search + ceiling)")
    all_results.extend(await test_bps_client())
    print()

    print("[5] Hook: validate_document")
    all_results.extend(test_hook_validate_document())
    print()

    print("[6] Hook: check_citation")
    all_results.extend(test_hook_check_citation())
    print()

    print("[7] HTTP utilities (cache, credentials)")
    all_results.extend(test_http_utils())
    print()

    print("[8] ANP client")
    all_results.extend(await test_anp_client())
    print()

    print("[9] SICRO client")
    all_results.extend(await test_sicro_client())
    print()

    print("[10] End-to-end workflows")
    all_results.extend(await test_e2e_workflows())
    print()

    # Summary
    passed = all_results.count(PASS)
    failed = all_results.count(FAIL)
    skipped = all_results.count(SKIP)
    total = len(all_results)

    print("=" * 60)
    print(f"Results: {passed}/{total} passed", end="")
    if failed:
        print(f", {failed} failed", end="")
    if skipped:
        print(f", {skipped} skipped", end="")
    print()
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    code = asyncio.run(main())
    sys.exit(code)
