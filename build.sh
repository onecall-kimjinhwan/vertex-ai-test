# build_and_push.sh
timestamp=$(date +%Y%m%d_%H%M%S)
docker build -t gcr.io/project/titanic-ml:$timestamp .
docker push gcr.io/project/titanic-ml:$timestamp

# GCS에 태그 저장
echo "gcr.io/project/titanic-ml:$timestamp" > latest_tag.txt
gsutil cp latest_tag.txt gs://hwaneehwanee2-bucket/container_tags/latest_tag.txt


===========

docker build -t onecall/titanic-ml:20250916-a8f3d2c .

docker tag onecall/titanic-ml:20250916-a8f3d2c asia-northeast3-docker.pkg.dev/rapid-pact-470904-u6/test/titanic-ml:20250916-a8f3d2c

docker push onecall/titanic-ml:20250916-a8f3d2c


