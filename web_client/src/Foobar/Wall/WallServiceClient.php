<?php
// GENERATED CODE -- DO NOT EDIT!

namespace Foobar\Wall;

/**
 */
class WallServiceClient extends \Grpc\BaseStub {

    /**
     * @param string $hostname hostname
     * @param array $opts channel options
     * @param \Grpc\Channel $channel (optional) re-use channel object
     */
    public function __construct($hostname, $opts, $channel = null) {
        parent::__construct($hostname, $opts, $channel);
    }

    /**
     * @param \Foobar\Wall\WallQuery $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function fetch(\Foobar\Wall\WallQuery $argument,
      $metadata = [], $options = []) {
        return $this->_serverStreamRequest('/foobar.wall.WallService/fetch',
        $argument,
        ['\Foobar\Posts\Post', 'decode'],
        $metadata, $options);
    }

    /**
     * @param \Foobar\Posts\Post $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function put(\Foobar\Posts\Post $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/foobar.wall.WallService/put',
        $argument,
        ['\Foobar\Shared\PBEmpty', 'decode'],
        $metadata, $options);
    }

}
