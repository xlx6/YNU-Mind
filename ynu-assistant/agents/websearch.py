from zhipuai import ZhipuAI

class WebSearchAgent:
    def __init__(self):
        self.client = ZhipuAI(api_key="")
    
    async def search(self, query):
        response = self.client.web_search.web_search(
            search_engine="search-std",
            search_query=query
        )
        return response.search_result[0].content