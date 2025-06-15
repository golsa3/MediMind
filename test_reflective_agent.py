from agents.reflective_agent import ReflectiveSummaryAgent

agent = ReflectiveSummaryAgent("data/sample_case.json")
reflection = agent.run()

print("\n=== Reflective Summary ===")
print(reflection)
