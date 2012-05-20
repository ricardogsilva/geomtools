PLUGINNAME = geomtools
UI_FILES = 
RESOURCE_FILES = 

default: compile
	
compile: $(UI_FILES) $(RESOURCE_FILES)

%.py : %.qrc
	pyrcc4 -o $@  $<

%.py : %.ui
	pyuic4 -o $@ $<

deploy: compile
	mkdir -p $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
	cp -vf *.py $(HOME)/.qgis/python/plugins/$(PLUGINNAME)

clean:
	rm -rf $(HOME)/.qgis/python/plugins/$(PLUGINNAME)
