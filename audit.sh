sleep 90
for p in /avocado-cream-in-kg/ /avocado-cream-in-kg-hindi/ /; do echo "$p $(curl -s https://mircglow.com$p | grep -c '1kg-tubs')"; done
echo "photo $(curl -s -o /dev/null -w '%{http_code}' https://mircglow.com/wp-content/uploads/2026/10/mirc-glow-avocado-cream-1kg-tubs.jpg)"
