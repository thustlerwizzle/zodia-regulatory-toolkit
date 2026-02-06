"""
Test script to verify NewsAPI key
"""
import requests
from datetime import datetime, timedelta

def test_newsapi_key(api_key):
    """Test if NewsAPI key is valid"""
    print("🔍 Testing NewsAPI Key...")
    print(f"Key: {api_key[:10]}...{api_key[-10:]}")
    print("-" * 70)
    
    # Test with a simple query
    test_query = "cryptocurrency regulation"
    
    # Calculate date range (last 7 days)
    to_date = datetime.now()
    from_date = to_date - timedelta(days=7)
    
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": test_query,
        "language": "en",
        "sortBy": "relevancy",
        "from": from_date.strftime("%Y-%m-%d"),
        "to": to_date.strftime("%Y-%m-%d"),
        "pageSize": 5,
        "apiKey": api_key
    }
    
    try:
        print(f"📡 Making request to NewsAPI...")
        print(f"Query: {test_query}")
        print(f"Date range: {from_date.strftime('%Y-%m-%d')} to {to_date.strftime('%Y-%m-%d')}")
        print()
        
        response = requests.get(url, params=params, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total_results = data.get("totalResults", 0)
            articles = data.get("articles", [])
            
            print("✅ API Key is VALID!")
            print(f"📊 Total results found: {total_results}")
            print(f"📄 Articles returned: {len(articles)}")
            print()
            
            if articles:
                print("📰 Sample Articles:")
                print("-" * 70)
                for i, article in enumerate(articles[:3], 1):
                    print(f"\n{i}. {article.get('title', 'N/A')}")
                    print(f"   Source: {article.get('source', {}).get('name', 'N/A')}")
                    print(f"   URL: {article.get('url', 'N/A')}")
                    print(f"   Published: {article.get('publishedAt', 'N/A')}")
            
            return True
            
        else:
            error_data = response.json()
            error_code = error_data.get("code", "unknown")
            error_message = error_data.get("message", "Unknown error")
            
            print("❌ API Key is INVALID or ERROR occurred")
            print(f"Error Code: {error_code}")
            print(f"Error Message: {error_message}")
            print()
            
            if error_code == "apiKeyInvalid":
                print("💡 This API key is invalid. Please check:")
                print("   - The key is correct")
                print("   - The key hasn't expired")
                print("   - You're using the right key type (free/paid)")
            elif error_code == "apiKeyMissing":
                print("💡 API key is missing from the request")
            elif error_code == "rateLimited":
                print("💡 You've exceeded the rate limit for your plan")
            elif error_code == "parametersMissing":
                print("💡 Required parameters are missing")
            
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network Error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    api_key = "69618ab7041b48188c9eb39b407b16f1"
    print("=" * 70)
    print("NewsAPI Key Test")
    print("=" * 70)
    print()
    
    result = test_newsapi_key(api_key)
    
    print()
    print("=" * 70)
    if result:
        print("✅ Test PASSED - API key is working!")
    else:
        print("❌ Test FAILED - API key has issues")
    print("=" * 70)

