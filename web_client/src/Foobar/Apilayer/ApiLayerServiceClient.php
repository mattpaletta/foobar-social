<?php
// GENERATED CODE -- DO NOT EDIT!

namespace Foobar\Apilayer;

/**
 */
class ApiLayerServiceClient extends \Grpc\BaseStub {

    /**
     * @param string $hostname hostname
     * @param array $opts channel options
     * @param \Grpc\Channel $channel (optional) re-use channel object
     */
    public function __construct($hostname, $opts, $channel = null) {
        parent::__construct($hostname, $opts, $channel);
    }

    /**
     * Authentication
     * @param \Foobar\Auth\Auth $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function login(\Foobar\Auth\Auth $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/foobar.apilayer.ApiLayerService/login',
        $argument,
        ['\Foobar\Auth\Token', 'decode'],
        $metadata, $options);
    }

    /**
     * Posts
     * @param \Foobar\Posts\Post $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function post(\Foobar\Posts\Post $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/foobar.apilayer.ApiLayerService/post',
        $argument,
        ['\Foobar\Posts\Post', 'decode'],
        $metadata, $options);
    }

    /**
     * Profile
     * @param \Foobar\Wall\WallQuery $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function get_wall(\Foobar\Wall\WallQuery $argument,
      $metadata = [], $options = []) {
        return $this->_serverStreamRequest('/foobar.apilayer.ApiLayerService/get_wall',
        $argument,
        ['\Foobar\Posts\Post', 'decode'],
        $metadata, $options);
    }

    /**
     * Timeline
     * @param \Foobar\Wall\WallQuery $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function get_news_feed(\Foobar\Wall\WallQuery $argument,
      $metadata = [], $options = []) {
        return $this->_serverStreamRequest('/foobar.apilayer.ApiLayerService/get_news_feed',
        $argument,
        ['\Foobar\Posts\Post', 'decode'],
        $metadata, $options);
    }

}
