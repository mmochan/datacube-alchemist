test:
	pytest tests

docker-test:
	docker build . --tag opendatacube/datacube-alchemist
	docker run opendatacube/datacube-alchemist -- pytest tests

push:
	docker build . --tag opendatacube/datacube-alchemist
	docker push opendatacube/datacube-alchemist

up:
	docker-compose up

initdb:
	docker-compose run alchemist \
		datacube system init

metadata:
	docker-compose run alchemist \
		datacube metadata add /opt/alchemist/metadata.eo_plus.yaml

product-sentinel2:
	docker-compose run alchemist \
		datacube product add https://raw.githubusercontent.com/GeoscienceAustralia/dea-config/master/dev/products/ga_s2_ard_nbar/ga_s2_ard_nbar_granule.yaml

add-failed-scene:
	docker-compose run alchemist \
		datacube dataset add s3://dea-public-data/L2/sentinel-2-nbar/S2MSIARD_NBAR/2019-01-08/S2B_OPER_MSI_ARD_TL_SGS__20190108T021617_A009609_T53HNE_N02.07/ARD-METADATA.yaml

run-one:
	docker-compose run alchemist \
		/opt/alchemist/cli.py run_one \
		/opt/alchemist/examples/fc_config_sentinel2b_test.yaml 95f69a40-ba51-43fd-b309-2a2a346bb485

shell:
	docker-compose run alchemist bash
