import os
import json
from agents.history_agent import HistoryAgent
from agents.diagnostic_agent import DiagnosticAgent
from agents.pharma_agent import PharmaAgent
from agents.reflective_agent import ReflectiveSummaryAgent
from agents.concern_agent import ConcernAgent

def run_all_agents(case_path):
    with open(case_path, "r") as file:
        case_data = json.load(file)

    results = {}
    results["history_summary"] = HistoryAgent(case_data).run()
    results["diagnostic_suggestions"] = DiagnosticAgent(case_data).run()
    results["medication_review"] = PharmaAgent(case_data).run()
    results["reflective_summary"] = ReflectiveSummaryAgent(case_data).run()
    results["concerns"] = ConcernAgent(case_data).run()

    return results
