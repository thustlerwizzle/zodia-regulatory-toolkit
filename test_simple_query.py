"""
Test with a simpler query
"""
from research_tools import ResearchTools

tools = ResearchTools()

# Test the exact query the agent uses
topic = "latest cryptocurrency and digital asset regulations 2024 2025"
query = f"{topic} regulation compliance policy"

print(f"Query being used: {query}")
print(f"Length: {len(query)} characters")
print()

# Test search_news directly
print("Testing search_news directly...")
results1 = tools.search_news(query, days=30)
print(f"Found {len(results1)} articles with full query")
print()

# Test with simpler query
print("Testing with simpler query...")
results2 = tools.search_news("cryptocurrency regulation", days=30)
print(f"Found {len(results2)} articles with simple query")
print()

# Test what search_regulatory_updates does
print("Testing search_regulatory_updates...")
results3 = tools.search_regulatory_updates(topic, jurisdiction=None)
print(f"Found {len(results3.get('news', []))} articles via search_regulatory_updates")
print(f"Errors: {results3.get('errors', [])}")

