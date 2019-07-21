import Dispatch
import SwiftGRPC
import Foundation

import SwiftRedis

struct Connection {
    let host: String
    let port: Int32
    
    init (host: String, port: Int32) {
        self.host = host
        self.port = port
    }
}

public enum PostImporterError : Error{
    case NoMessage
}

class PostImporter : Foobar_PostImporter_PostImporterServiceProvider {
    
    private var redis: Redis
    private let IMPORT_QUEUE: String!
    private let POST_INCREMENT_KEY: String!
    
    init(redis: Connection) {
        let env = ProcessInfo.processInfo.environment
        guard let import_queue = env["IMPORT_QUEUE"] else {
            print("Failed to get IMPORT_QUEUE from env")
            exit(1)
        }
        guard let post_increment_key = env["POST_INCREMENT_KEY"] else {
            print("Failed to get POST_INCREMENT_KEY from env")
            exit(1)
        }
        
        self.IMPORT_QUEUE = import_queue
        self.POST_INCREMENT_KEY = post_increment_key
        
        self.redis = Redis()
        self.redis.connect(host: redis.host, port: redis.port) { (redisError: NSError?) in
            if let error = redisError {
                print(error)
                exit(1)
            } else {
                print("Connected to redis")
            }
        }
    }
    
    func create_post(request: Foobar_Posts_Post, session: Foobar_PostImporter_PostImporterServicecreate_postSession) throws -> Foobar_Shared_Empty {
        
        // Verify post
        let has_msg = request.msg != ""
        let has_username = !request.username.isEmpty
        let has_location = request.hasLoc &&
            !request.loc.long.isZero &&
            !request.loc.long.isNaN &&
            !request.loc.lat.isZero &&
            !request.loc.lat.isZero &&
            request.loc.lat > -90 &&
            request.loc.lat < 90 &&
            request.loc.long > -180 &&
            request.loc.long < 180

        if !has_msg {
            print("post has no message")
            throw PostImporterError.NoMessage
        }
        
        if !has_username {
            print("No username")
            throw NSError(domain: "No Username", code: 1, userInfo: [:])
        }
        
        // TODO: Verify that username exists
        
        var did_error = false
        
        self.redis.incr(self.POST_INCREMENT_KEY) { (next_id, error) in
            if error != nil {
                print("failed to increment redis key", error!.localizedDescription)
                did_error = true
                return
            }
            
            var post = Foobar_Posts_Post()
            
            guard let id = next_id else {
                return
            }
            // Construct the new post
            
            // Add in the incremented post_id and the datetime on the server
            post.msg = request.msg
            post.id = Int64(id)
            post.username = request.username
            post.datetime = Int64(Date().timeIntervalSince1970)

            // If not a complete location, or invalid, don't include it
            if !has_location {
                post.clearLoc()
            } else {
                post.loc = request.loc
            }
            
            do {
                let json = try post.jsonString()
//                print("pushing: \(json)")
                self.redis.lpush(self.IMPORT_QUEUE, values: RedisString(json), callback: { (_, error) in
                    if error != nil {
                        print("print from failed redis push", error!.localizedDescription)
                        did_error = true
                    }
                })
            } catch {
                print("Failed pushing into redis", error.localizedDescription)
                session.cancel()
            }
        }
        
        if did_error {
            throw NSError(domain: "Unknown Error", code: 1, userInfo: [:])
        }
        
        return Foobar_Shared_Empty()
    }
}

gRPC.initialize()
let inst = PostImporter(redis: Connection(host: "post_importer_redis", port: 6379))
let address = "0.0.0.0:9000"
print("Starting server in \(address)")
let server = ServiceServer(address: address,
                           serviceProviders: [inst])
server.start()
//while true {
//    sleep(60 * 60 * 24)
//}
dispatchMain()
