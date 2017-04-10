PROGRAM=mrlg
VERSION=5.5.0
DISTRIB=DESCRIPTION LICENSE INSTALL Makefile fastping2 ztr ztraceroute index.cgi mrlg.conf.sample 

all: 
	@echo "Read INSTALL first..."	

distrib:clean
	@(echo $(PROGRAM) is version ${VERSION}; \
	mkdir $(PROGRAM)-${VERSION}; \
	cp $(DISTRIB) $(PROGRAM)-${VERSION};\
	tar cvf $(PROGRAM)-${VERSION}.tar $(PROGRAM)-${VERSION}; \
	rm -rf $(PROGRAM)-${VERSION}; \
	gzip --verbose --best --force $(PROGRAM)-${VERSION}.tar)

clean:
	-rm -f *~ *.o fastping
