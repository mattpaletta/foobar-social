#!/usr/bin/env bash

root="$(pwd)"
folders=(users create_user token_dispenser auth user_setting friends_db friends posts news_feed news_feed_data_access news_feed_merge post_importer profile wall apilayer web_client)
for folder in "${folders[@]}"; do
  echo "$folder"
  cd $folder

  sh kube_deploy.sh
  did_deploy=$?

  cd "$root"

  if [[ did_deploy -gt 0 ]]; then
    echo "Failed to deploy"
    break
  fi

  sleep 10
done