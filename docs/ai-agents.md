# AI Product Intelligence Agents

ShopPilot uses OpenAI for seller-facing recommendations. All agents are grounded in collected marketplace data.

## Configuration

Set `OPENAI_API_KEY` in `.env`. Without it, agents return structured mock recommendations.

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
- Missing API key → clear message + mock fallback
