# snip

Local code snippet manager. Zero dependencies.

## Usage

```bash
# Add snippets
snip.py add "http-server" -l python -t "web,quick" -c "python3 -m http.server 8000"
echo "SELECT * FROM users;" | snip.py add "all-users" -l sql -t "db"

# Retrieve
snip.py get "http-server"
snip.py get "http" --raw  # fuzzy match, raw output

# Browse
snip.py list
snip.py list --lang python --tag web

# Search
snip.py search "server"

# Export
snip.py export          # markdown
snip.py export --json   # JSON

# Delete
snip.py rm "http-server"
```

## Features

- **Fuzzy name matching** on `get`
- **Tags + language** filtering
- **Scored search** across name, description, tags, and code
- **Pipe-friendly** — stdin input, raw output
- Stored in `~/.local/share/snip/snippets.json`

## Philosophy

One file. Zero deps. Does one thing well.
