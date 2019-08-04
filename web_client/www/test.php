<?php

require 'vendor/autoload.php';
require 'src/GPBMetadata/Apilayer.php';
require 'src/Foobar/Apilayer/ApiLayerServiceClient.php';
require 'src/GPBMetadata/Auth.php';
require 'src/GPBMetadata/Posts.php';
require 'src/GPBMetadata/Wall.php';
require 'src/Foobar/Auth/Auth.php';
require 'src/Foobar/Auth/Token.php';
require 'src/Foobar/Posts/Post.php';
require 'src/Foobar/Wall/WallQuery.php';

$client = new Foobar\ApiLayer\ApilayerServiceClient('api-layer:50051', ['credentials' => Grpc\ChannelCredentials::createInsecure(),]);

$auth_obj = new Foobar\Auth\Auth();
$auth_obj->setUsername("fake");
$auth_obj->setPassword("password");

list($token, $status) = $client->login($auth_obj)->wait();

print_r($status);
