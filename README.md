# New Install Notifier

**New Install Notifier** is a Slack Bolt app that connects to NYC Mesh's [MeshDB](https://github.com/nycmeshnet/meshdb) via webhook and automatically posts new install requests to designated channels on the [NYC Mesh workspace](https://slack.nycmesh.net).  

1. **MeshDB** sends a `install.created` webhook whenever a new install request is submitted.
2. **New Install Notifier** receives the webhook, processes the install data, and checks which node(s) the install belongs to.
3. Based on your configuration in `channels.json`, it posts a message to the corresponding **Slack channel**.

---

## How to Setup

### 1. Create a Webhook in MeshDB
Follow the MeshDB documentation here: [How to onboard API clients to MeshDB](https://wiki.nycmesh.net/books/6-services-software/page/how-to-onboard-api-clients-to-meshdb#bkmrk-adding-a-new-webhook)

When creating your webhook:
- **User:** Use the user you created following the MeshDB guide.
- **Target URL:** The public endpoint where this app is hosted (e.g., yourserver.com/webhook)
- **Event:** `install.created`  

---

### 2. Configure Channels

In your project directory, edit `channels.json` to map node IDs to Slack channels.  
Each entry defines:
- The **node ID** (as a string key)
- The **channel ID** (from Slack)
- A **description** (for reference)

Example `channels.json`:

```json
{
    "5107": {
        "channel_id": "C09D83P1E1G",
        "description": "Daniel's Test"
    },
    "3461": {
        "channel_id": "C06CPH118V7",
        "description": "PH Fiber"
    },
    "333": {
        "channel_id": "G0FS2EVSQ",
        "description": "50th Street"
    },
    "1932": {
        "channel_id": "C02LZR9KKUP",
        "description": "GSG Fiber"
    },
    "1933": {
        "channel_id": "C02LZR9KKUP",
        "description": "GSG Fiber"
    },
    "1934": {
        "channel_id": "C02LZR9KKUP",
        "description": "GSG Fiber"
    },
    "1936": {
        "channel_id": "C02LZR9KKUP",
        "description": "GSG Fiber (165 Broome)"
    }
}
