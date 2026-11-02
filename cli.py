"""
Command Line Interface for Agentic DevSecOps Copilot
Author: Shruti Bawase
"""

import sys
import json
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
from agent.sre_agent import SREAutonomousAgent

console = Console()

def run_cli():
    console.print(Panel.fit(
        "[bold cyan]🤖 Agentic DevSecOps Copilot[/bold cyan]\n"
        "[dim]Model Context Protocol (MCP) | Enterprise SRE RAG | Autonomous Remediation[/dim]\n"
        "[italic green]Designed by Shruti Bawase[/italic green]",
        border_style="cyan"
    ))

    agent = SREAutonomousAgent()
    alert_input = "CRITICAL: Pod payment-api OOMKilled in namespace payment-tier with exit code 137"

    console.print(f"\n[bold yellow]📥 Incoming Production Alert:[/bold yellow] {alert_input}\n")

    with console.status("[bold green]Executing MCP cluster inspection & RAG knowledge search...[/bold green]"):
        diagnosis = agent.diagnose_incident(alert_input)
        remediation_pr = agent.generate_self_healing_pr(diagnosis)

    # Render Root Cause Table
    table = Table(title="🔍 Autonomous Root-Cause Analysis", show_lines=True)
    table.add_column("Category", style="cyan", width=22)
    table.add_column("Telemetry & Insight", style="white")

    table.add_row("Root Cause", diagnosis["root_cause"])
    table.add_row("Telemetry Source", diagnosis["live_telemetry_source"])
    table.add_row("Live Cluster Drift", json.dumps(diagnosis["infrastructure_drift"], indent=2))
    table.add_row("Matched RAG Runbook", f"{diagnosis['matched_rag_runbooks'][0]['title']} (Score: {diagnosis['matched_rag_runbooks'][0]['score']})")
    table.add_row("Recommended Fix", diagnosis["recommended_action"])

    console.print(table)

    # Render Remediation PR
    console.print(f"\n[bold magenta]🚀 Self-Healing Pull Request Generated:[/bold magenta] [bold white]{remediation_pr['pr_title']}[/bold white]")
    console.print(f"[dim]Branch: {remediation_pr['branch']} | Status: {remediation_pr['status']}[/dim]\n")

    syntax = Syntax(remediation_pr["diff"], "diff", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Git Patch Diff", border_style="magenta"))

if __name__ == "__main__":
    run_cli()
