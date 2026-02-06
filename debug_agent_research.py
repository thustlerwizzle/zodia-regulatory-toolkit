"""
Debug script to see what research results the agent receives
"""
from research_tools import ResearchTools
from regulatory_agent import RegulatoryAgent

print("=" * 70)
print("Debug: Agent Research Results")
print("=" * 70)

# Initialize tools
tools = ResearchTools()
agent = RegulatoryAgent()

# Test query
query = "latest cryptocurrency and digital asset regulations 2024 2025"
print(f"\n📊 Query: {query}")
print()

# Get research results
print("🔍 Getting research results...")
results = tools.search_regulatory_updates(
    topic=query,
    jurisdiction=None
)

print(f"\n📈 Research Results Summary:")
print(f"   News articles: {len(results.get('news', []))}")
print(f"   Errors: {len(results.get('errors', []))}")
if results.get('errors'):
    for error in results.get('errors', []):
        print(f"      - {error}")

print(f"\n📰 News Articles Found:")
print("-" * 70)
for i, article in enumerate(results.get('news', [])[:5], 1):
    print(f"\n{i}. {article.get('title', 'N/A')}")
    print(f"   Content length: {len(article.get('content', ''))} chars")
    print(f"   URL: {article.get('url', 'N/A')[:60]}...")
    print(f"   Published: {article.get('published_at', 'N/A')}")

# Check what the agent sees
print(f"\n🔍 What Agent Sees:")
print("-" * 70)
all_content = []
for source_type in ["news"]:
    for result in results.get(source_type, []):
        content = f"Title: {result.get('title', '')}\n"
        content += f"Content: {result.get('content', '')}\n"
        content += f"URL: {result.get('url', '')}\n"
        all_content.append(content)

combined_content = "\n\n---\n\n".join(all_content)
print(f"Combined content length: {len(combined_content)} characters")
print(f"Has content: {len(combined_content.strip()) >= 50}")

if len(combined_content.strip()) < 50:
    print("\n⚠️  Content is too short - agent will show 'Limited research results' message")
    print(f"   This might be because article descriptions are empty or very short")
else:
    print("\n✅ Content is sufficient - agent should process it")

print()
print("=" * 70)

