# AI Product Intelligence Agents

ShopPilot uses OpenAI for seller-facing recommendations. All agents are grounded in collected marketplace data.

## Configuration

Set `OPENAI_API_KEY` in `.env`. AI endpoints return an error if the key is missing or the request fails.

## Agents

### ListingAdvisorAgent
- **Input:** listing, competitors, pricing/keyword summaries
- **Output:** improved title, description, tags, pricing, positioning

### ProductExpansionAgent
- **Input:** all listings, trends, competitors
- **Output:** product ideas with rationale and price ranges

### MarketResearchAgent
- **Input:** analysis summary
- **Output:** market summary, competitor/pricing insights, risks

### FreeformAgent
- **Input:** analysis data + user question
- **Output:** grounded answer with evidence and uncertainty notes

## Grounding Rules

- Agents receive only data from the current analysis
- They must not invent competitor facts
- Missing API key → API returns a clear error
