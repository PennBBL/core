curl -X POST -H "Content-Type: application/json" -H "Accept: application/json" -H "Travis-API-Version: 3" -H "User-Agent: Flywheel ci" -H "Authorization: token $1" -d '{"request": {"branch":"master"}}' https://api.travis-ci.com/repo/flywheel-io%2Finstaller/requests
