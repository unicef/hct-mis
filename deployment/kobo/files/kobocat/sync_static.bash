#!/bin/bash
set -e

mkdir -p "${KOBOCAT_SRC_DIR}/onadata/static"
chown -R "${UWSGI_USER}" "${KOBOCAT_SRC_DIR}/onadata/static"

echo "Collecting static files..."
gosu "${UWSGI_USER}" "${VIRTUAL_ENV}/bin/python" manage.py collectstatic -v 0 --noinput
echo "Done"

# `chown -R` becomes very slow once a fair amount of media has been collected,
# so reset ownership of the media directory *only*. See #379, #449
#
# Commenting out due to persistent volume read only issue
#
#echo "Resetting ownership of media directory..."
#chown "${UWSGI_USER}" "${KOBOCAT_SRC_DIR}/media"
#echo "Done."
#echo '%%%%%%% NOTICE %%%%%%%'
#echo '% To avoid long delays, we no longer reset ownership *recursively*'
#echo '% every time this container starts. If you have trouble with'
#echo '% permissions, please run the following command inside the'
#echo '% KoBoCAT container:'
#echo "%	chown -R \"${UWSGI_USER}\" \"${KOBOCAT_SRC_DIR}\""
#echo '%%%%%%%%%%%%%%%%%%%%%%'

echo "Syncing to nginx folder..."
rsync -aq --delete --chown=www-data "${KOBOCAT_SRC_DIR}/onadata/static/" "${NGINX_STATIC_DIR}/"
echo "Done"
