# front-caddy TLS certs

Drop the Cloudflare **Origin Certificate** for the ecosystem here. These files
are gitignored (`*.pem`, `*.key`) — never commit them.

Generate in Cloudflare → the `alpinepost.app` zone → **SSL/TLS → Origin Server
→ Create Certificate**, with hostnames `*.alpinepost.app` and `alpinepost.app`.

Save the two blocks as:

- `origin.pem` — the **Origin Certificate** block
- `origin.key` — the **Private Key** block

The Caddyfile references them as:

```
tls /etc/caddy/certs/origin.pem /etc/caddy/certs/origin.key
```

(this `caddy/` dir is mounted to `/etc/caddy/certs` in docker-compose.yml).
Also set the zone's SSL/TLS mode to **Full (Strict)**.
