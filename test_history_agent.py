from agents.history_agent import HistoryAgent

agent = HistoryAgent("data/sample_case.json")
summary = agent.run()
print("\n=== History Summary ===")
print(summary)
