sleep 100
S=https://mircglow.com
curl -s $S/sitemap.xml | grep -o '<loc>[^<]*' | sed 's/<loc>//' > urls.txt
echo "pages in sitemap: $(wc -l < urls.txt)"
bad=0; while read u; do c=$(curl -s -o /dev/null -w '%{http_code}' "$u"); [ "$c" != 200 ] && { echo "$c $u"; bad=$((bad+1)); }; done < urls.txt; echo "not working: $bad"
