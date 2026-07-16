# `cpa.config.json` schema

Mirrors `cna.config.json` from Create-Node-App with Python-oriented fields.

```json
{
  "name": "fastapi-starter",
  "customOptions": [
    {
      "key": "projectName",
      "type": "string",
      "message": "Project name",
      "default": "my-app"
    }
  ]
}
```

Parse errors raise `CPA_CONFIG_PARSE`.
