import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)


class WebSearch:
      """
          Performs web searches using DuckDuckGo (no API key required).
              Extracts clean text results to pass back to GPT-4.
                  """

    DDGS_URL = "https://html.duckduckgo.com/html/"
    HEADERS = {
              "User-Agent": "Mozilla/5.0 (compatible; PersonalAssistant/1.0)"
    }

    def search(self, query: str, max_results: int = 5) -> dict:
              """
                      Search the web for the given query.
                              Returns a list of results with title, url, and snippet.
                                      """
              try:
                            params = {"q": query, "kl": "en-us"}
                            response = requests.post(
                                self.DDGS_URL,
                                data=params,
                                headers=self.HEADERS,
                                timeout=10
                            )
                            response.raise_for_status()

                  soup = BeautifulSoup(response.text, "lxml")
            results = []

            for result in soup.select(".result")[:max_results]:
                              title_el = result.select_one(".result__title")
                              snippet_el = result.select_one(".result__snippet")
                              url_el = result.select_one(".result__url")

                if title_el and snippet_el:
                                      results.append({
                                                                "title": title_el.get_text(strip=True),
                                                                "snippet": snippet_el.get_text(strip=True),
                                                                "url": url_el.get_text(strip=True) if url_el else ""
                                      })

            if not results:
                              return {"results": [], "message": f"No results found for: {query}"}

            logger.info(f"Web search for '{query}' returned {len(results)} results")
            return {"query": query, "results": results, "count": len(results)}

except Exception as e:
            logger.error(f"Web search error: {e}")
            return {"error": str(e), "query": query}

    def get_page_content(self, url: str, max_chars: int = 2000) -> dict:
              """
                      Fetch and extract text content from a specific URL.
                              Useful for reading articles referenced in search results.
                                      """
        try:
                      response = requests.get(url, headers=self.HEADERS, timeout=10)
                      response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")

            # Remove scripts and styles
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                              tag.decompose()

            text = soup.get_text(separator=" ", strip=True)
            # Truncate to max_chars
            if len(text) > max_chars:
                              text = text[:max_chars] + "..."

            return {"url": url, "content": text, "length": len(text)}

except Exception as e:
            logger.error(f"Error fetching page {url}: {e}")
            return {"error": str(e), "url": url}
