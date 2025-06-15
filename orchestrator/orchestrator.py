import os
from agents.history_agent import HistoryAgent
from agents.diagnostic_agent import DiagnosticAgent
from agents.pharma_agent import PharmaAgent
from agents.reflective_agent import ReflectiveSummaryAgent
from agents.concern_agent import ConcernAgent

def run_all_agents(case_path):
    results = {}

    # Run HistoryAgent
    history_agent = HistoryAgent(case_path)
    results["history_summary"] = history_agent.run()

    # Run DiagnosticAgent
    diagnostic_agent = DiagnosticAgent(case_path)
    results["diagnostic_suggestions"] = diagnostic_agent.run()

    # Run PharmaAgent
    pharma_agent = PharmaAgent(case_path)
    results["medication_review"] = pharma_agent.run()

    # Run ReflectiveSummaryAgent
    reflective_agent = ReflectiveSummaryAgent(case_path)
    results["reflective_summary"] = reflective_agent.run()

    # Run ConcernAgent
    concern_agent = ConcernAgent(case_path)
    results["concern_flags"] = concern_agent.run()

    return results
