#!/bin/bash
# Live payment / checkout switches on each store (read-only GETs)
for u in https://youthfacebeautycream.com/api/config https://glutanex.co.in/api/config https://www.fairnpink.in/api/config https://www.youthfacebeauty.com/api/payment-config; do
  echo "== $u"; curl -sS -m 20 -L "$u" -w "\nHTTP %{http_code}\n"; done
for u in https://theglutathione.com/ https://mircglow.com/ https://youthfacebeautycream.com/ https://glutanex.co.in/ https://www.fairnpink.in/ https://www.youthfacebeauty.com/; do
  echo "== $u $(curl -sS -m 20 -L -o /tmp/p.html -w '%{http_code}' "$u")"; grep -oiE 'checkout\.razorpay\.com|razorpay|cash on delivery|wa\.me/[0-9]+|/api/(create-order|cod-order)' /tmp/p.html | sort | uniq -c | head -6; done
