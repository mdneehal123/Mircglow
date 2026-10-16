sleep 100
S=https://mircglow.com
for p in /category/skincare-guides/page/3/ /avocado-night-cream-side-effects/feed/ /night-cream-for-men/feed/ /comments/feed/ /category/skincare-guides/feed/ /product/glutathione-cream/feed/ /product/avocado-night-cream/feed/ /glass-skin-routine-steps-for-a-smooth-hydrated-looking-glow/feed/ /author/mircglow/feed/ /category/uncategorized/feed/ /feed/ /night-cream-for-men/; do
 echo "$p -> $(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' $S$p) | final $(curl -s -L -o /dev/null -w '%{http_code}' $S$p)"; done
