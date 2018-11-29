#!/usr/bin/env sh
set -eu

# /etc/hosts is corrupted if it has lines starting with tab.
# Exit to allow docker to restart.
if grep $'^\t' /etc/hosts; then
    echo "Host mapping in /etc/hosts is buggy, fail container start."
    exit 1
fi

# Set RUNAS_USER based on the owner of the persistent data path.
export RUNAS_USER=$(stat -c '%u' $SCITRAN_PERSISTENT_DATA_PATH)

# Create prometheus multiproc dir at startup
export prometheus_multiproc_dir=/var/prometheus
mkdir -p ${prometheus_multiproc_dir}
chown -R ${RUNAS_USER} ${prometheus_multiproc_dir}
chown -R ${RUNAS_USER} ${SCITRAN_PERSISTENT_DATA_PATH}

# Run $PRE_RUNAS_CMD as root if provided. Useful for things like JIT pip installs.
[ -n "${PRE_RUNAS_CMD:-}" ] && eval $PRE_RUNAS_CMD

# Use exec to keep PID and use su-exec (gosu equivalent) to step-down from root.
exec su-exec ${RUNAS_USER} "$@"
