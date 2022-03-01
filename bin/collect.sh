#!/bin/bash

ENV=${VIRTUAL_ENV:-env}
LIB=$ENV/lib
PYTHON=`ls $LIB`
SITE_PACKAGES=$LIB/$PYTHON/site-packages/

SOURCES=(
    "$SITE_PACKAGES/rijkshuisstijl/static/rijkshuisstijl/components"
    "$SITE_PACKAGES/rijkshuisstijl/static/rijkshuisstijl/fonts"
)
TARGET=src/sdg/static/

if [ -z "${PYTHON}" ]; then
    echo "Please set VIRTUAL_ENV (or activate your environment)".
    exit 1
fi

for s in ${SOURCES[@]}
do
    echo "Copying: $s"
    cp -r $s $TARGET
done
echo "Done!"


