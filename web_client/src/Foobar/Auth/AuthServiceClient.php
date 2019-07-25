<?php
// GENERATED CODE -- DO NOT EDIT!

namespace Foobar\Auth;

/**
 */
class AuthServiceClient extends \Grpc\BaseStub {

    /**
     * @param string $hostname hostname
     * @param array $opts channel options
     * @param \Grpc\Channel $channel (optional) re-use channel object
     */
    public function __construct($hostname, $opts, $channel = null) {
        parent::__construct($hostname, $opts, $channel);
    }

    /**
     * @param \Foobar\Auth\Auth $argument input argument
     * @param array $metadata metadata
     * @param array $options call options
     */
    public function check_auth(\Foobar\Auth\Auth $argument,
      $metadata = [], $options = []) {
        return $this->_simpleRequest('/foobar.auth.AuthService/check_auth',
        $argument,
        ['\Foobar\Auth\Token', 'decode'],
        $metadata, $options);
    }

}
