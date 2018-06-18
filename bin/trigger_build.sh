TRAVIS_TOKEN=$1
TRIGGER_IMAGE=$2
TARGET_REPO=$3
MESSAGE="Build triggered by image:$TRIGGER_IMAGE"
POST_DATA="{\"request\": {\"branch\":\"ci_trigger\", \"message\":\"$MESSAGE\", \"config\": {\"env\": {\"CORE_IMAGE\": \"$TRIGGER_IMAGE\"}}}}"
curl -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Travis-API-Version: 3" -H "User-Agent: Flywheel ci" -H "Authorization: token $TRAVIS_TOKEN" -d "$POST_DATA" https://api.travis-ci.com/repo/$TARGET_REPO/requests
