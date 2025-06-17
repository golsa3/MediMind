import os
from agents.history_agent import HistoryAgent
from agents.diagnostic_agent import DiagnosticAgent
from agents.pharma_agent import PharmaAgent
from agents.reflective_agent import ReflectiveSummaryAgent
from agents.concern_agent import ConcernAgent

def run_all_agents(case_data: dict):
    results = {}

    history_agent = HistoryAgent(case_data)
    results["history_summary"] = history_agent.run()

    diagnostic_agent = DiagnosticAgent(case_data)
    results["diagnostic_suggestions"] = diagnostic_agent.run()

    pharma_agent = PharmaAgent(case_data)
    results["medication_review"] = pharma_agent.run()

    reflective_agent = ReflectiveSummaryAgent(case_data)
    results["reflective_summary"] = reflective_agent.run()

    concern_agent = ConcernAgent(case_data)
    results["concerns"] = concern_agent.run()

    return results
