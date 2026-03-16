# Synapse Connector Plugin Architecture

Synapse is designed to be **100% Tenant Agnostic**. While our built-in connectors handle standard platforms (Zendesk, Confluence, Public Web), specialized enterprise knowledge centers (KBs) may require custom handling.

## Built-in Connectors
1. **ZendeskConnector**: Uses the Zendesk Help Center API with configurable locales.
2. **ConfluenceConnector**: Uses the Confluence Cloud API (supports Bearer tokens).
3. **WebsiteConnector**: A non-blocking crawler that respects domain/path boundaries and parses `sitemap.xml` for discovery.
4. **DocumentConnector**: Fetches and parses PDF/Markdown/Text files via HTTP.

## Handling Specialized KBs
If a tenant's knowledge source falls into one of these categories, you can extend the system using our **Connector Plugin Architecture**:

### 1. KBs Behind Authentication
For sites requiring Login/SSO, create a new connector class in `graph-generator/connectors/` that implements the `BaseConnector` interface and uses a headless browser or specialized auth headers.

### 2. JS-Heavy (SPA) Websites
If a site requires JavaScript execution (React/Vue/Angular) to render content, you can swap the `httpx` + `BeautifulSoup` stack in a custom connector for a headless browser (e.g., Playwright or Selenium).

### 3. Protected Enterprise APIs
If the content stays within a proprietary system (e.g., ServiceNow, Sharepoint), a dedicated connector can be written to use those specific APIs while keeping the rest of the Synapse pipeline identical.

## "Zero Adaptation" Philosophy
By using the **Graph Generator Configuration**, new connectors can be registered and assigned to specific tenants without changing the core Synapse Agent or Dashboard logic. This ensures that the system scales to any enterprise environment with configuration only.
