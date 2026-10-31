"""Database operations, table coupling, and data reconciliation analyzer."""
import re
from typing import List, Dict, Any


def analyze_database_interactions(file_inventory: List[Dict[str, Any]], findings: List[Any]) -> Dict[str, Any]:
    """Extract database tables, queries, and direct writers."""
    tables_found: Dict[str, Dict[str, Any]] = {}
    stored_procedures: List[str] = []

    # Patterns for SQL tables
    table_pattern = re.compile(r'(?i)(?:FROM|JOIN|INTO|UPDATE|TABLE)\s+([A-Za-z0-9_]+)')
    proc_pattern = re.compile(r'(?i)CREATE\s+PROCEDURE\s+([A-Za-z0-9_]+)')

    for f in file_inventory:
        if f["extension"] in (".sql", ".py", ".java", ".cbl", ".cob"):
            try:
                with open(f["path"], "r", encoding="utf-8", errors="replace") as file_obj:
                    content = file_obj.read()
                    
                    # Extract tables
                    for match in table_pattern.finditer(content):
                        table = match.group(1).upper()
                        if table in {"SELECT", "WHERE", "SET", "VALUES", "GROUP", "ORDER", "BY", "INNER", "LEFT", "RIGHT", "OUTER"}:
                            continue
                        if table not in tables_found:
                            tables_found[table] = {"writers": set(), "readers": set()}
                        
                        if any(w in match.group(0).upper() for w in ["INTO", "UPDATE"]):
                            tables_found[table]["writers"].add(f["relative_path"])
                        else:
                            tables_found[table]["readers"].add(f["relative_path"])

                    # Extract stored procedures
                    for pmatch in proc_pattern.finditer(content):
                        stored_procedures.append(pmatch.group(1))
            except Exception:
                continue

    # Format shared tables
    shared_tables = []
    for t_name, data in tables_found.items():
        if len(data["writers"]) > 1 or (len(data["writers"]) >= 1 and len(data["readers"]) >= 2):
            shared_tables.append({
                "table": t_name,
                "writers_count": len(data["writers"]),
                "readers_count": len(data["readers"]),
                "writers": list(data["writers"]),
                "risk": "High direct-write contention across independent modules"
            })

    return {
        "tables": {k: {"writers": list(v["writers"]), "readers": list(v["readers"])} for k, v in tables_found.items()},
        "shared_tables": shared_tables,
        "stored_procedures": stored_procedures,
        "total_tables": len(tables_found)
    }

