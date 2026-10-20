#!/bin/bash
# Order Desk public product list (read-only)
curl -sS -m 20 -L "https://skinday.shop/api/catalog" -w "\nHTTP %{http_code}\n"
