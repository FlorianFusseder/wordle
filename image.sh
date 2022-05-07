#!/bin/zsh

if [ "$1" = "backend" ]; then
  build_name="wordle-backend-ff"
  folder_name="backend"
elif [ "$1" = "frontend" ]; then
  build_name="wordle-frontend-ff"
  folder_name="frontend"
  npm run build --prefix ./"${folder_name}"
else
  echo "No known service with name '${1}', exiting..."
  return 0
fi

echo "release $build_name"

docker build -t wordle-"${folder_name}" -f "${folder_name}"/Dockerfile .
docker tag wordle-"${folder_name}" registry.heroku.com/"${build_name}"/web
if [ "$2" != "--release" ]; then
  echo "Skip release, exiting..."
  return 0
fi
docker push registry.heroku.com/"${build_name}"/web
sha=$(docker inspect registry.heroku.com/"${build_name}"/web --format={{.Id}})
curl --netrc -X PATCH https://api.heroku.com/apps/"${build_name}"/formation \
  -d '{
        "updates": [
          {
            "type": "web",
            "docker_image": "'"${sha}"'"
          }
        ]
      }' \
  -H "Content-Type: application/json" \
  -H "Accept: application/vnd.heroku+json; version=3.docker-releases"

heroku open --app="${build_name}"
