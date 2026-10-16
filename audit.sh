sleep 100
S=https://mircglow.com
for p in /avocado-night-cream-original/ /avocado-night-cream-review/ /product/avocado-night-cream/ /wp-content/uploads/2026/10/mirc-glow-avocado-night-cream-benefits-how-to-use.mp4; do echo "$p $(curl -s -o /dev/null -w '%{http_code} %{content_type}' $S$p)"; done
echo "video entries in sitemap: $(curl -s $S/sitemap.xml | grep -c '<video:video>')"
