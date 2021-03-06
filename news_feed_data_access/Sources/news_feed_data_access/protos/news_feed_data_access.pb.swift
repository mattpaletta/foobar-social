// DO NOT EDIT.
//
// Generated by the Swift generator plugin for the protocol buffer compiler.
// Source: news_feed_data_access.proto
//
// For information on using the generated types, please see the documenation:
//   https://github.com/apple/swift-protobuf/

import Foundation
import SwiftProtobuf

// If the compiler emits an error on this type, it is because this file
// was generated by a version of the `protoc` Swift plug-in that is
// incompatible with the version of SwiftProtobuf to which you are linking.
// Please ensure that your are building against the same version of the API
// that was used to generate this file.
fileprivate struct _GeneratedWithProtocGenSwiftVersion: SwiftProtobuf.ProtobufAPIVersionCheck {
  struct _2: SwiftProtobuf.ProtobufAPIVersion_2 {}
  typealias Version = _2
}

struct Foobar_NewsFeedDataAccess_NewsFeedPost {
  // SwiftProtobuf.Message conformance is added in an extension below. See the
  // `Message` and `Message+*Additions` files in the SwiftProtobuf library for
  // methods supported on all messages.

  /// User of the news feed
  var user: String {
    get {return _storage._user}
    set {_uniqueStorage()._user = newValue}
  }

  var post: Foobar_Posts_Post {
    get {return _storage._post ?? Foobar_Posts_Post()}
    set {_uniqueStorage()._post = newValue}
  }
  /// Returns true if `post` has been explicitly set.
  var hasPost: Bool {return _storage._post != nil}
  /// Clears the value of `post`. Subsequent reads from it will return its default value.
  mutating func clearPost() {_uniqueStorage()._post = nil}

  var unknownFields = SwiftProtobuf.UnknownStorage()

  init() {}

  fileprivate var _storage = _StorageClass.defaultInstance
}

// MARK: - Code below here is support for the SwiftProtobuf runtime.

fileprivate let _protobuf_package = "foobar.news_feed_data_access"

extension Foobar_NewsFeedDataAccess_NewsFeedPost: SwiftProtobuf.Message, SwiftProtobuf._MessageImplementationBase, SwiftProtobuf._ProtoNameProviding {
  static let protoMessageName: String = _protobuf_package + ".NewsFeedPost"
  static let _protobuf_nameMap: SwiftProtobuf._NameMap = [
    1: .same(proto: "user"),
    2: .same(proto: "post"),
  ]

  fileprivate class _StorageClass {
    var _user: String = String()
    var _post: Foobar_Posts_Post? = nil

    static let defaultInstance = _StorageClass()

    private init() {}

    init(copying source: _StorageClass) {
      _user = source._user
      _post = source._post
    }
  }

  fileprivate mutating func _uniqueStorage() -> _StorageClass {
    if !isKnownUniquelyReferenced(&_storage) {
      _storage = _StorageClass(copying: _storage)
    }
    return _storage
  }

  mutating func decodeMessage<D: SwiftProtobuf.Decoder>(decoder: inout D) throws {
    _ = _uniqueStorage()
    try withExtendedLifetime(_storage) { (_storage: _StorageClass) in
      while let fieldNumber = try decoder.nextFieldNumber() {
        switch fieldNumber {
        case 1: try decoder.decodeSingularStringField(value: &_storage._user)
        case 2: try decoder.decodeSingularMessageField(value: &_storage._post)
        default: break
        }
      }
    }
  }

  func traverse<V: SwiftProtobuf.Visitor>(visitor: inout V) throws {
    try withExtendedLifetime(_storage) { (_storage: _StorageClass) in
      if !_storage._user.isEmpty {
        try visitor.visitSingularStringField(value: _storage._user, fieldNumber: 1)
      }
      if let v = _storage._post {
        try visitor.visitSingularMessageField(value: v, fieldNumber: 2)
      }
    }
    try unknownFields.traverse(visitor: &visitor)
  }

  static func ==(lhs: Foobar_NewsFeedDataAccess_NewsFeedPost, rhs: Foobar_NewsFeedDataAccess_NewsFeedPost) -> Bool {
    if lhs._storage !== rhs._storage {
      let storagesAreEqual: Bool = withExtendedLifetime((lhs._storage, rhs._storage)) { (_args: (_StorageClass, _StorageClass)) in
        let _storage = _args.0
        let rhs_storage = _args.1
        if _storage._user != rhs_storage._user {return false}
        if _storage._post != rhs_storage._post {return false}
        return true
      }
      if !storagesAreEqual {return false}
    }
    if lhs.unknownFields != rhs.unknownFields {return false}
    return true
  }
}
