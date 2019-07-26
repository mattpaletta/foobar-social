<?php
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: shared.proto

namespace Foobar\Shared;

use Google\Protobuf\Internal\GPBType;
use Google\Protobuf\Internal\RepeatedField;
use Google\Protobuf\Internal\GPBUtil;
use Google\Protobuf\Internal\GPBWrapperUtils;

/**
 * Generated from protobuf message <code>foobar.shared.Location</code>
 */
class Location extends \Google\Protobuf\Internal\Message
{
    /**
     * Generated from protobuf field <code>float lat = 1;</code>
     */
    private $lat = 0.0;
    /**
     * Generated from protobuf field <code>float long = 2;</code>
     */
    private $long = 0.0;

    /**
     * Constructor.
     *
     * @param array $data {
     *     Optional. Data for populating the Message object.
     *
     *     @type float $lat
     *     @type float $long
     * }
     */
    public function __construct($data = NULL) {
        \GPBMetadata\Shared::initOnce();
        parent::__construct($data);
    }

    /**
     * Generated from protobuf field <code>float lat = 1;</code>
     * @return float
     */
    public function getLat()
    {
        return $this->lat;
    }

    /**
     * Generated from protobuf field <code>float lat = 1;</code>
     * @param float $var
     * @return $this
     */
    public function setLat($var)
    {
        GPBUtil::checkFloat($var);
        $this->lat = $var;

        return $this;
    }

    /**
     * Generated from protobuf field <code>float long = 2;</code>
     * @return float
     */
    public function getLong()
    {
        return $this->long;
    }

    /**
     * Generated from protobuf field <code>float long = 2;</code>
     * @param float $var
     * @return $this
     */
    public function setLong($var)
    {
        GPBUtil::checkFloat($var);
        $this->long = $var;

        return $this;
    }

}
