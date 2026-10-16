sleep 100
S=https://mircglow.com
for p in night-cream-side-effects is-night-cream-necessary night-cream-vs-moisturizer night-cream-for-teenagers night-cream-benefits night-cream-for-normal-skin night-cream-for-acne-marks-and-dark-spots night-cream-in-your-20s night-cream-for-tanned-skin night-cream-ke-fayde-aur-nuksan night-cream-din-mein-laga-sakte-hain night-cream-kab-lagana-chahiye product-category/night-creams; do echo "$p $(curl -s -o /dev/null -w '%{http_code}' $S/$p/)"; done
echo "title: $(curl -s $S/product-category/night-creams/ | grep -o '<title>[^<]*')"
echo "sitemap: $(curl -s $S/sitemap.xml | grep -c '<loc>')"
