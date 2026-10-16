sleep 100
S=https://mircglow.com
curl -s $S/sitemap.xml | grep -o '<loc>[^<]*' | sed 's/<loc>//' > urls.txt
echo "sitemap: $(wc -l < urls.txt)"
bad=0; while read u; do c=$(curl -s -o /dev/null -w '%{http_code}' "$u"); [ "$c" != 200 ] && { echo "$c $u"; bad=$((bad+1)); }; done < urls.txt; echo "non-200: $bad"
for p in winter-skincare-routine-india night-cream-in-kg-ahmedabad kojic-acid-side-effects glass-skin-kaise-paye; do echo "$p $(curl -s -o /dev/null -w '%{http_code}' $S/$p/)"; done
