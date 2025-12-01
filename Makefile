generate: data/temp/all.nt
	python bin/generate.py

generate+serve_locally: data/temp/all.nt
	python bin/generate.py --site_url http://localhost:8000 --serve

data/stats.ttl: data/berlin_core_orgs.ttl
	@echo "generating VOID statistics from $^..."
	@echo "writing to $@ ..."
	@python bin/void_statistics.py \
		--input $^ \
		--base_uri "https://berlin.github.io/lod-core-organigram/" \
		--base_prefix "coreorg" \
		--dataset_uri "https://berlin.github.io/lod-core-organigram/" > $@

data/temp/all.nt: data/temp void.ttl \
	data/berlin_core_orgs.ttl data/stats.ttl \
	sources/vocab/org.ttl
	@echo "combining $(filter-out $<,$^) to $@ ..."
	@rdfpipe -o ntriples $(filter-out $<,$^) > $@

install_templates:
	python bin/install_templates.py

clean: clean-temp

clean-temp:
	@echo "deleting temp folder ..."
	@rm -rf data/temp

data/temp:
	@echo "creating temp directory ..."
	@mkdir -p $@

# ---------

data/abbreviations.json: data/org_names.json
	cat $< | jq '.names | map(select(length == 1)) | map({(.[0]): ""}) | add' > $@

data/org_list.csv: data/berlin_core_orgs.ttl
	arq --query queries/list-orgs.rq --data $< --data sources/vocab/org.ttl --results=CSV > $@