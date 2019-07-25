<?php
// GENERATED CODE -- DO NOT EDIT!

namespace Foobar\Posts;

/**
 */
class PostServiceClient extends \Grpc\BaseStub {

    /**
     * @param string $hostname hostname
     * @param array $opts channel options
     * @param \Grpc\Channel $channel (optional) re-use channel object
     */
    public function __construct($hostname, $opts, $channel = null) {
        parent::__construct($hostname, $opts, $channel);
    }

    /**
     * @param \Foobar\Posts\PostQuery $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function get_posts(\Foobar\Posts\PostQuery $argument,
      $metadata = [], $options = []) {
        return $this->_serverStreamRequest('/foobar.posts.PostService/get_posts',
        $argument,
        ['\Foobar\Posts\Post', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \Foobar\Posts\Post $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function fetch(\Foobar\Posts\Post $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/foobar.posts.PostService/fetch',
        $argument,
        ['\Foobar\Posts\Post', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \Foobar\Posts\Post $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function create_post(\Foobar\Posts\Post $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/foobar.posts.PostService/create_post',
        $argument,
        ['\Foobar\Shared\PBEmpty', 'decode'],
        $metadata, $options);
    }

}
