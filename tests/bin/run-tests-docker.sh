#!/usr/bin/env sh

set -eu
unset CDPATH
cd "$( dirname "$0" )/../.."


USAGE="
Usage:
    $0 [OPTION...] [-- TEST_ARGS...]

Build scitran-core image and run tests in a Docker container.

Options:
    -h, --help          Print this help and exit

    -B, --no-build      Skip rebuilding default Docker image
    --image IMAGE       Use custom Docker image
    -- TEST_ARGS        Arguments passed to tests/bin/run-tests-ubuntu.sh

"

main() {
    local DOCKER_IMAGE=
    local TEST_ARGS=
    local MONGO_VERSION=3.2

    while [ $# -gt 0 ]; do
        case "$1" in
            -B|--no-build)
                DOCKER_IMAGE="scitran-core:run-tests"
                ;;
            --image)
                DOCKER_IMAGE="$2"
                shift
                ;;
            --)
                shift
                TEST_ARGS="$@"
                break
                ;;
            -h|--help)
                printf "$USAGE" >&2
                exit 0
                ;;
            *)
                printf "Invalid argument: $1\n" >&2
                printf "$USAGE" >&2
                exit 1
                ;;
        esac
        shift
    done

    # Docker build
    if [ -z "${DOCKER_IMAGE}" ]; then
        log "Building scitran-core:run-tests ..."
        docker build -t scitran-core:run-tests .
    else
        docker tag "$DOCKER_IMAGE" "scitran-core:run-tests"
    fi

    trap clean_up EXIT

    docker network create scitran-core-test-network

    # Launch core + mongo
    local SCITRAN_CORE_DRONE_SECRET=T+27oHSKw+WQqT/rre+iaiIY4vNzav/fPStHqW/Eczk=

    docker run -d \
        --name scitran-core-test-service \
        --network scitran-core-test-network \
        --volume $(pwd)/api:/src/core/api \
        --volume $(pwd)/tests:/src/core/tests \
        --env SCITRAN_CORE_DRONE_SECRET=$SCITRAN_CORE_DRONE_SECRET \
        --env SCITRAN_RUNTIME_COVERAGE=true \
        --env SCITRAN_CORE_ACCESS_LOG_ENABLED=true \
        scitran-core:run-tests

    # Execute tests
    docker run -it \
        --name scitran-core-test-runner \
        --network scitran-core-test-network \
        --volume $(pwd)/api:/src/core/api \
        --volume $(pwd)/tests:/src/core/tests \
        --env SCITRAN_CORE_DRONE_SECRET=$SCITRAN_CORE_DRONE_SECRET \
        --env SCITRAN_PERSISTENT_DB_URI=mongodb://scitran-core-test-service:27017/scitran \
        --env SCITRAN_PERSISTENT_DB_LOG_URI=mongodb://scitran-core-test-service:27017/logs \
        --env SCITRAN_SITE_API_URL=http://scitran-core-test-service/api \
        scitran-core:run-tests \
        /src/core/tests/bin/run-tests-ubuntu.sh \
        $TEST_ARGS
}


clean_up() {
    local TEST_RESULT_CODE=$?
    set +e

    log "INFO: Test return code = $TEST_RESULT_CODE"
    if [ "${TEST_RESULT_CODE}" = "0" ]; then
        # Copy unit test coverage
        docker cp scitran-core-test-runner:/src/core/.coverage .coverage.unit-tests

        # Gracefully stop API then copy integration test coverage
        # TODO added exec to dev+mongo.sh and tried (TERM|KILL|INT|QUIT) signals to no avail
        # Somehow api.web.start/save_coverage() (atexit) is NOT triggered
        # docker kill --signal=SIGTERM scitran-core-test-service
        # docker cp scitran-core-test-service:/src/core/.coverage.integration-tests ./

        # TODO report/combine/htmlize coverage using a test container
    else
        log "INFO: Printing container logs..."
        docker logs scitran-core-test-service
        log "ERROR: Test return code = $TEST_RESULT_CODE. Container logs printed above."
    fi

    # Spin down dependencies
    docker rm -f -v scitran-core-test-runner
    docker rm -f -v scitran-core-test-service
    docker network rm scitran-core-test-network
    exit $TEST_RESULT_CODE
}


log() {
    printf "\n%s\n" "$@" >&2
}


main "$@"
