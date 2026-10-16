sleep 100
curl -s https://mircglow.com/best-night-cream-for-glowing-skin/ -o h; echo "status $(curl -s -o /dev/null -w '%{http_code}' https://mircglow.com/best-night-cream-for-glowing-skin/) title: $(grep -o '<title>[^<]*' h) quickpicks: $(grep -c 'quick picks' h)"
