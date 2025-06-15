from orchestrator.orchestrator import run_all_agents

case_path = "data/sample_case.json"
results = run_all_agents(case_path)

print("\n=== MediMind Case Review ===")

print("\n🩺 History Summary:")
print(results["history_summary"])

print("\n🧠 Diagnostic Suggestions:")
for dx in results["diagnostic_suggestions"]:
    print("- " + dx)

print("\n💊 Medication Review:")
for issue in results["medication_review"]:
    print(issue)

print("\n📋 Reflective Summary:")
print(results["reflective_summary"])

print("\n🚨 Concerns / Questions:")
for flag in results["concern_flags"]:
    print(flag)
