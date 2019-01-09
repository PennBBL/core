#!/usr/bin/env sh

set -eu
unset CDPATH
cd "$( dirname "$0" )/.."
ROOT_DIR="$(pwd)/.."

USAGE="
Usage:
    $0 [OPTION...] [-- PYTEST_ARGS...]

Build flywheel/core image and run tests in a Docker container.
Also displays coverage report and saves HTML under htmlcov/

Options:
    -h, --help            Print this help and exit

    -B, --no-build        Skip rebuilding default Docker image
        --image IMAGE     Use custom Docker image
        --shell           Enter shell instead of running tests
        --python2         Use python2 image instead of python3

    -- PYTEST_ARGS      Arguments passed to py.test

"

TEST_PREFIX=sdk-test

main() {
    local DOCKER_IMAGE=
    local PYTEST_ARGS=
    local RUN_SHELL=
    local SDK_IMAGE=python:3.4

    while [ $# -gt 0 ]; do
        case "$1" in
            -h|--help)
                log "$USAGE"
                exit 0
                ;;
            -B|--no-build)
                DOCKER_IMAGE="core:testing"
                BUILD_SDK_IMAGE=false
                ;;
            --python2)
                SDK_IMAGE=python:2.7
                ;;
            --image)
                DOCKER_IMAGE="$2"
                shift
                ;;
            --shell)
                RUN_SHELL=true
                ;;
            --)
                shift
                PYTEST_ARGS="$@"
                break
                ;;
            *)
                log "Invalid argument: $1"
                log "$USAGE"
                exit 1
                ;;
        esac
        shift
    done

    # Docker build
    if [ -z "${DOCKER_IMAGE}" ]; then
        log "Building core:testing ..."
        docker build -t core:testing ..
    else
        docker tag "$DOCKER_IMAGE" "core:testing"
    fi

    trap clean_up EXIT
    docker network create ${TEST_PREFIX}

    # Launch core test service (includes mongo)
    docker run -d \
        --name ${TEST_PREFIX}-service \
        --network ${TEST_PREFIX} \
        --volume ${ROOT_DIR}/api:/var/scitran/code/api/api \
        --volume ${ROOT_DIR}/tests:/var/scitran/code/api/tests \
        --volume ${ROOT_DIR}/logging_conf.yml:/logging/logging_conf.yml \
        --env PRE_RUNAS_CMD='[ "$1" = gunicorn ] && mongod --bind_ip_all > /dev/null 2>&1 &' \
        --env SCITRAN_CORE_DRONE_SECRET=secret \
        --env SCITRAN_CORE_ACCESS_LOG_ENABLED=true \
        --env FLYWHEEL_LOGGING=/logging/logging_conf.yml \
        --env SYSLOG_HOST=localhost \
        --env SYSLOG_PORT=514 \
        core:testing gunicorn --reload --workers=1 --log-file=/tmp/core.log \
                -c /src/core/gunicorn_config.py api.app

    # Run core test cmd
    local SDK_TEST_CMD
    [ $RUN_SHELL ] && SDK_TEST_CMD=bash || \
                      SDK_TEST_CMD="scripts/tests.sh -- $PYTEST_ARGS"
    docker run -it \
        --name ${TEST_PREFIX}-runner \
        --network ${TEST_PREFIX} \
        --volume $(pwd):/var/scitran/code/sdk \
        --env SCITRAN_SITE_API_URL=http://${TEST_PREFIX}-service:8080/api \
        --env SCITRAN_PERSISTENT_DB_URI=mongodb://${TEST_PREFIX}-service:27017/scitran \
        --env SCITRAN_CORE_DRONE_SECRET=secret \
        --env FLYWHEEL_SDK_SKIP_VERSION_CHECK=1 \
        -w /var/scitran/code/sdk \
        ${SDK_IMAGE} \
        $SDK_TEST_CMD
}


clean_up() {
    local TEST_RESULT_CODE=$?
    set +e

    log "INFO: Test return code = $TEST_RESULT_CODE"
    if [ "${TEST_RESULT_CODE}" = "0" ]; then
        #log "INFO: Collecting coverage..."

        # Copy unit test coverage
        #docker cp ${TEST_PREFIX}-runner:/var/scitran/code/api/.coverage .coverage.unit-tests

        # TODO: Save integration test coverage?
        docker wait $(docker stop ${TEST_PREFIX}-service)
    else
        log "INFO: Printing container logs..."
        docker logs ${TEST_PREFIX}-service
        log "ERROR: Test return code = $TEST_RESULT_CODE. Container logs printed above."
    fi

    # Spin down core service
    docker rm --force --volumes ${TEST_PREFIX}-runner
    docker rm --force --volumes ${TEST_PREFIX}-service
    docker network rm ${TEST_PREFIX}
    exit $TEST_RESULT_CODE
}


log() {
    printf "\n%s\n" "$@" >&2
}


main "$@"
