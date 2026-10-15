set +e
S=https://mircglow.com
echo "== Sitemap URLs: status / redirects / size / time"
curl -s $S/sitemap.xml | grep -o '<loc>[^<]*' | sed 's/<loc>//' > urls.txt
echo "count: $(wc -l < urls.txt)"
while read u; do curl -s -o /dev/null -w "%{http_code} %{num_redirects} %{size_download} %{time_total} $u\n" "$u"; done < urls.txt > st.txt
echo "non-200: $(awk '$1!=200' st.txt | wc -l)"; awk '$1!=200' st.txt | head
echo "slowest:"; sort -k4 -nr st.txt | head -3
echo "largest html:"; sort -k3 -nr st.txt | head -3
echo "== Redirect tests"
for p in "http://mircglow.com/" "https://www.mircglow.com/" "https://www.mircglow.com/shop/" "$S/shop" "$S/SHOP/" "$S/cart/" "$S/home/" "$S/?p=1" "$S/feed/" "$S/wp-admin/" "$S/wp-login.php" "$S/sitemap_index.xml" "$S/product-sitemap.xml" "$S/index.html" "$S/blog/page/2/" "$S/product/radiance-renewal-serum/" "$S/does-not-exist-xyz/"; do
  echo "$p -> $(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' "$p")"; done
echo "== Headers"
for p in "/" "/product/glass-glow-cream/" "/assets/$(curl -s $S/ | grep -o 'site\.[a-f0-9]*\.css' | head -1)" "/wp-content/uploads/2026/10/mirc-glow-glass-glow-cream-glutathione-30g.mg.webp"; do
  echo "-- $p"; curl -s -I -H 'Accept-Encoding: br,gzip' "$S$p" | grep -iE '^(HTTP|content-type|content-encoding|cache-control|strict|x-content|x-vercel-cache|content-length|age)'; done
echo "== robots/llms/feed"
for p in /robots.txt /llms.txt /feed.xml /74d314fcd13a092ae512fe4c12566f9f.txt; do echo "$p $(curl -s -o /dev/null -w '%{http_code} %{content_type}' $S$p)"; done
echo "== Lighthouse (mobile)"
for p in "/" "/product/glass-glow-cream/" "/avocado-cream/" "/avocado-cream-for-oily-skin/"; do
  npx -y lighthouse@12.2.1 "$S$p" --quiet --only-categories=performance,accessibility,best-practices,seo --form-factor=mobile --output=json --output-path=lh.json --chrome-flags="--headless=new --no-sandbox" >/dev/null 2>&1
  node -e '
const r=require("./lh.json");const c=r.categories,a=r.audits;
console.log("-- '"$p"'", Object.keys(c).map(k=>k+":"+Math.round(c[k].score*100)).join(" "),
 "| LCP",a["largest-contentful-paint"].displayValue,"CLS",a["cumulative-layout-shift"].displayValue,"TBT",a["total-blocking-time"].displayValue,"FCP",a["first-contentful-paint"].displayValue);
for (const k of ["accessibility","best-practices","seo","performance"]) for (const ref of c[k].auditRefs){const x=a[ref.id]; if(x&&x.score!==null&&x.score<0.9&&ref.weight>0) console.log("   ["+k+"] "+x.id+": "+x.title+(x.displayValue?" ("+x.displayValue+")":""));}
'; done
