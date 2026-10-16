sleep 90
S=https://mircglow.com
for p in /product/glass-glow-cream/ /night-cream-in-kg-mumbai/ /product-category/night-creams/ /avocado-cream/ /llms.txt; do
 curl -s $S$p -o h
 echo "$p $(curl -s -o /dev/null -w '%{http_code}' $S$p) quick:$(grep -c 'class="quick"' h) strike:$(grep -c StrikethroughPrice h) service:$(grep -c '"@type":"Service"' h) hindi-in-llms:$(grep -c 'Hindi guides' h)"
done
