sleep 90
for p in avocado-korean-night-cream avocado-night-cream; do curl -s https://mircglow.com/product/$p/ -o h; echo "$p amazon-block:$(grep -c 'id=\"h-amz\"' h) rating-line:$(grep -c 'class=\"rl ' h) ext-link:$(grep -c 'amazon.in/s' h)"; done
