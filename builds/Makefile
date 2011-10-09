build:
	echo "<html><title>Intermediate builds</title><body><h1>Intermediate builds</h1><body>" > index.html
	find . -name \*.vba -type f | sort -n | while read f; do newsection=$$(basename $$(dirname "$$f")); if [ "$$newsection" != "$$section" ]; then [ -n "$$section" ] && echo "</ul>"; section="$$newsection"; echo "$$section<ul>"; fi; echo "<li><a href='$$f'>$$(basename $$f)</a></li>"; done >> index.html
	echo "</ul></body></html>" >> index.html
