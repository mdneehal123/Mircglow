S=https://mircglow.com
curl -s $S/sitemap.xml | grep -o '<loc>[^<]*' | sed 's/<loc>//' > urls.txt
echo "pages in sitemap: $(wc -l < urls.txt)"
bad=0; while read u; do c=$(curl -s -o /dev/null -w '%{http_code}' "$u"); [ "$c" != 200 ] && { echo "$c $u"; bad=$((bad+1)); }; done < urls.txt; echo "not working: $bad"
for p in / /product/glass-glow-cream/ /product/glass-glow-night-duo/ /product/avocado-glow-cream-15g/ /avocado-cream-in-kg/ /avocado-cream-in-kg-hindi/; do echo "$p $(curl -s -o /dev/null -w '%{http_code}' $S$p)"; done
curl -s $S/ | grep -c 'fk-hero' | sed 's/^/new home page: /'
