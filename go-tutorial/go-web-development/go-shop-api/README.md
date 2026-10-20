# Go Shop API (Go Web Development course)

```bash
go mod init shop-api && go mod tidy
go run .
curl -s localhost:3000/api/v1/products
curl -s -X POST localhost:3000/api/v1/products -H 'X-Api-Key: secret-123' -H 'Content-Type: application/json' \
  -d '{"name":"Redmi 13","brand":"Xiaomi","price":17500,"stock":5}'
```
