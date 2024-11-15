.PHONY: deploy

GIT_DIR := /opt/ckan-catalog/data.naturalcapitalproject.stanford.edu

# Building happens first, while the cluster is still up, because it can take a while.
# This way we minimize catalog downtime.
deploy:
	git log origin/master..HEAD > /dev/null || (echo "There are unpushed commits.  git push and re-run."; exit 1)
	gcloud compute ssh --zone "us-central1-a" "ckan-1" --project "sdss-natcap-gef-ckan" \
		--command="sudo sh -c 'cd $(GIT_DIR) && git pull && docker compose build && docker compose down && docker compose up --detach --remove-orphans'"
