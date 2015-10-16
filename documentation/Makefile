diagram: diagram.png

diagram.png: diagram.txt
	if [ -n "$(shell which ditaa)" ]; then ditaa $^ $@; elif [ -f ditaa0_9.jar ]; then java -jar ditaa0_9.jar $^ $@; else echo "Unable to find ditaa, please install ditaa or download ditaa0_9.jar (http://ditaa.sf.net/)and place it in folder documentation"; exit 1 ; fi

clean:
	@rm -f diagram.png

.PHONY: diagram clean
