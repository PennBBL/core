TRAVIS_TOKEN=$1
MESSAGE="Build triggered by repo:core branch:$2"
POST_DATA="{\"request\": {\"branch\":\"ci_trigger\", \"message\":\"$MESSAGE\"}}"
curl -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Travis-API-Version: 3" -H "User-Agent: Flywheel ci" -H "Authorization: token $TRAVIS_TOKEN" -d "$POST_DATA" https://api.travis-ci.com/repo/flywheel-io%2Finstaller/requests
