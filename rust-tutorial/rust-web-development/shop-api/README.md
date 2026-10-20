# Shop API (Rust Web Development course)

```bash
cp .env.example .env
cargo run
curl -s localhost:3000/api/v1/products
curl -s -X POST localhost:3000/api/v1/products -H 'x-api-key: secret-123' -H 'Content-Type: application/json' \
  -d '{"name":"Redmi 13","brand":"Xiaomi","price":17500,"stock":5}'
```
