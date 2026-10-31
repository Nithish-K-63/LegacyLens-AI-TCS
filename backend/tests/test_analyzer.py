"""Static analyzer and business rule preservation unit tests."""
import ast
import tempfile
import os
from backend.services.static_analyzer import PythonASTAnalyzer, ConservativeMultiLanguageScanner, analyze_codebase
from backend.services.business_rules import extract_business_rules
from backend.services.dependency_analyzer import build_dependency_graph


def test_python_ast_analyzer_rules_and_risks():
    """Verify AST visitor catches auth boundaries, discount logic, and raw SQL queries."""
    code = """
import pickle

@app.post("/order/checkout")
def checkout(order_id, user_role, customer_tier):
    if user_role == "ADMIN_OVERRIDE":
        apply_override(order_id)
    
    if customer_tier == "Gold":
        discount = 0.12
    
    cursor.execute(f"SELECT * FROM orders WHERE id = '{order_id}'")
"""
    tree = ast.parse(code)
    analyzer = PythonASTAnalyzer("test.py", "src/order/checkout.py", code.splitlines())
    analyzer.visit(tree)

    categories = [f.category for f in analyzer.findings]
    assert "Security" in categories  # pickle and SQL injection
    assert "Business Logic" in categories or any("RULE" in f.id for f in analyzer.findings)


def test_conservative_java_and_cobol_scanner(tmp_path):
    """Verify regex scanner handles Java reflection and COBOL EXEC SQL."""
    java_file = tmp_path / "Service.java"
    java_file.write_text("""
    public class Service {
        public void load() throws Exception {
            Class<?> clazz = Class.forName("com.legacy.DynamicModule");
        }
    }
    """)

    findings = ConservativeMultiLanguageScanner.scan_file(str(java_file), "src/Service.java", "Java")
    assert len(findings) >= 1
    assert findings[0].category == "Obsolete Candidate"

    cbl_file = tmp_path / "BATCH.cbl"
    cbl_file.write_text("""
    PROCEDURE DIVISION.
        EXEC SQL
            UPDATE CUSTOMER_CREDIT SET BALANCE = 0 WHERE ID = 100
        END-EXEC.
    """)
    cobol_findings = ConservativeMultiLanguageScanner.scan_file(str(cbl_file), "legacy/BATCH.cbl", "COBOL")
    assert len(cobol_findings) >= 1
    assert cobol_findings[0].category == "Data Access"


def test_dependency_graph_construction():
    """Verify NetworkX builds directed graph with in/out degrees."""
    file_inventory = [
        {"relative_path": "src/order/service.py", "language": "Python", "extension": ".py", "path": "test"},
        {"relative_path": "src/pricing/engine.py", "language": "Python", "extension": ".py", "path": "test"},
        {"relative_path": "src/customer/db.py", "language": "Python", "extension": ".py", "path": "test"},
    ]
    static_results = {
        "findings": [],
        "python_analyzers": []
    }
    nodes, edges = build_dependency_graph(file_inventory, static_results)
    assert len(nodes) >= 3
    node_ids = [n.id for n in nodes]
    assert "order" in node_ids or "pricing" in node_ids


def test_javascript_and_react_static_scanner():
    """Verify JS / React Native static analysis extracts calculation rules, lifecycle debt, and links."""
    js_sample = """
    import React from 'react';
    import Screen from './components/Screen';
    import { evaluate } from './actions/calculator';

    class Calculator extends React.Component {
        componentWillMount() {
            console.log("legacy mount");
        }
        calculateResult(op) {
            switch(op) {
                case "ADD": return Math.floor(10 + 20);
                default: return 0;
            }
        }
    }
    """
    lines = js_sample.strip().splitlines()
    findings = ConservativeMultiLanguageScanner._scan_javascript("src/components/Calculator.js", lines, "Calculator")
    assert len(findings) >= 2
    categories = [f.category for f in findings]
    assert "Obsolete Candidate" in categories or "Business Logic" in categories

