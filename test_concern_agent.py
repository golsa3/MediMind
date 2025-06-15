from agents.concern_agent import ConcernAgent

agent = ConcernAgent("data/sample_case.json")
concerns = agent.run()

print("\n=== Concern Agent Review ===")
for issue in concerns:
    print(issue)
