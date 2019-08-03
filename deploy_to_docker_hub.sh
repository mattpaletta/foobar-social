#!/usr/bin/env bash
source venv/bin/activate
#make all -B
docker-compose build
did_build=$?
if [ $did_build -eq 0 ]
then
  echo "Built containers successfully!"
else
  exit $did_build
fi

containers=( $(docker images | awk '{print $1;}' | grep ^foobar-social) )
#echo $containers

for img in "${containers[@]}"
do
#  echo "Pushing: $img\n"
  docker tag "$img":latest mattpaletta/"$img":latest
  docker push mattpaletta/"$img":latest
done