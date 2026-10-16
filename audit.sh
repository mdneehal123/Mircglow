sleep 100
S=https://mircglow.com
for p in avocado-night-cream-for-pigmentation-prone-skin avocado-night-cream-for-men avocado-night-cream-in-your-20s avocado-and-kojic-acid-explained avocado-cream-for-sensitive-skin-in-summer how-to-spot-fake-avocado-whitening-creams; do echo "$p $(curl -s -o /dev/null -w '%{http_code}' $S/$p/)"; done
curl -s $S/product/avocado-night-cream/ -o h; echo "product: reviews-box $(grep -c 'Write a review on WhatsApp' h) hindi $(grep -c 'id=\"hindi\"' h) compare $(grep -c 'all-avocado-creams' h)"
echo "sitemap: $(curl -s $S/sitemap.xml | grep -c '<loc>')"
