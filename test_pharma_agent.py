from agents.pharma_agent import PharmaAgent

agent = PharmaAgent("data/sample_case.json")
results = agent.run()

print("\n=== PharmaAgent Report ===")
for item in results:
    print(item)
