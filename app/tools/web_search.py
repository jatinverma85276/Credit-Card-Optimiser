"""
Web search tool for finding product prices using Tavily API
"""
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
import re
import os

# Initialize Tavily search with API key
os.environ["TAVILY_API_KEY"] = "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"
tavily_search = TavilySearchResults(max_results=5)

@tool
def search_product_price(product_name: str) -> str:
    """
    Search for product price online using Tavily API
    
    Args:
        product_name: Name of the product to search for (e.g., "iPhone 15", "MacBook Pro M3")
    
    Returns:
        str: Search results containing price information
    """
    try:
        # Add "price in India" to get more relevant results
        query = f"{product_name} price in India"
        results = tavily_search.invoke(query)
        
        # Tavily returns a list of dicts with 'content' and 'url'
        # Combine all content into a single string
        combined_results = ""
        for result in results:
            if isinstance(result, dict) and 'content' in result:
                combined_results += result['content'] + "\n"
        
        return combined_results if combined_results else str(results)
    except Exception as e:
        return f"Error searching for price: {str(e)}"

def extract_price_from_search(search_results: str, product_name: str) -> float:
    """
    Extract price from search results using regex patterns
    
    Args:
        search_results: Raw search results text
        product_name: Product name for context
    
    Returns:
        float: Extracted price in rupees, or 0 if not found
    """
    try:
        # Common price patterns in Indian rupees
        patterns = [
            r'₹\s*([0-9,]+)',  # ₹50,000
            r'Rs\.?\s*([0-9,]+)',  # Rs. 50000 or Rs 50,000
            r'INR\s*([0-9,]+)',  # INR 50000
            r'Price:\s*₹?\s*([0-9,]+)',  # Price: ₹50000
            r'MRP:\s*₹?\s*([0-9,]+)',  # MRP: ₹50000
            r'₹([0-9]+(?:,[0-9]+)*)',  # ₹79900 or ₹79,900
        ]
        
        prices = []
        for pattern in patterns:
            matches = re.findall(pattern, search_results, re.IGNORECASE)
            for match in matches:
                # Remove commas and convert to float
                price_str = match.replace(',', '')
                try:
                    price = float(price_str)
                    # Filter out unrealistic prices (too low or too high)
                    if 100 < price < 10000000:  # Between ₹100 and ₹1 crore
                        prices.append(price)
                except ValueError:
                    continue
        
        if prices:
            # Return the most common price (mode) or median
            from statistics import median
            return median(prices)
        
        return 0
    except Exception as e:
        print(f"Error extracting price: {e}")
        return 0
