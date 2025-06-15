from agents.diagnostic_agent import DiagnosticAgent

agent = DiagnosticAgent("data/sample_case.json")
results = agent.run()

print("\n=== Diagnostic Suggestions ===")
for diagnosis in results:
    print("- " + diagnosis)
