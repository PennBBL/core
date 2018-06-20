TRAVIS_TOKEN=$1
ORIGIN_IMAGE=$2
TARGET_REPO=$3
TARGET_BRANCH=$4
ORIGIN_BRANCH=$5
ORIGIN_TAG=$6
if [[ -n $ORIGIN_TAG ]]; then
    ORIGIN_TAG=$ORIGIN_TAG
    ORIGIN_GIT_REF=$ORIGIN_TAG
    ORIGIN_IMAGE_REF=$ORIGIN_TAG
else
    if [[ ${ORIGIN_BRANCH} == "master" ]]; then
        ORIGIN_IMAGE_REF="latest"
    else
        ORIGIN_IMAGE_REF="$ORIGIN_BRANCH.latest"
    fi
    ORIGIN_TAG=""
    ORIGIN_GIT_REF="origin/$ORIGIN_BRANCH"
fi
MESSAGE="Build triggered by image:$ORIGIN_IMAGE"
POST_DATA="{\"request\": {\"branch\":\"$TARGET_BRANCH\", \"message\":\"$MESSAGE\", \"config\": {\"env\": {\"CORE_IMAGE\": \"$ORIGIN_IMAGE\", \"ORIGIN_GIT_REF\": \"$ORIGIN_GIT_REF\", \"ORIGIN_IMAGE_REF\": \"$ORIGIN_IMAGE_REF\", \"ORIGIN_TAG\": \"$ORIGIN_TAG\"}}}}"
curl -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Travis-API-Version: 3" -H "User-Agent: Flywheel ci" -H "Authorization: token $TRAVIS_TOKEN" -d "$POST_DATA" https://api.travis-ci.com/repo/$TARGET_REPO/requests