import Dispatch
import SwiftGRPC
import Foundation

import SwiftKueryPostgreSQL
import SwiftRedis

struct Connection {
    let host: String
    let port: Int32
    
    init (host: String, port: Int32) {
        self.host = host
        self.port = port
    }
}

class NewsFeedDataAccess : Foobar_NewsFeedDataAccess_NewsFeedDataAccessServiceProvider {
    
    private var redis: Redis
    private var postgres: PostgreSQLConnection
    
    private let MAX_USER_TIMELINE_CACHE_SIZE = 100
    
    init(redis: Connection, psql: Connection) {
        self.redis = Redis()
        self.redis.connect(host: redis.host, port: redis.port) { (redisError: NSError?) in
            if let error = redisError {
                print(error)
            }
        }
        
        /*
         ConnectionOptions an optional set of:
         options - command-line options to be sent to the server
         databaseName - the database name
         userName - the user name
         password - the user password
         connectionTimeout - maximum wait for connection in seconds. Zero or not specified means wait indefinitely.
         */
        self.postgres = PostgreSQLConnection(host: psql.host, port: psql.port, options: nil)
        self.postgres.connect() { result in
            guard result.success else {
                print(result.asError)
                // Connection not established, handle error
                return
            }
            // Connection established
        }
    }
    
    private func connect_to(redis: Connection) {
        
//            } else {
//                print("Connected to Redis")
//                // Set a key
//                redis.set("Redis", value: "on Swift") { (result: Bool, redisError: NSError?) in
//                    if let error = redisError {
//                        print(error)
//                    }
//                    // Get the same key
//                    redis.get("Redis") { (string: RedisString?, redisError: NSError?) in
//                        if let error = redisError {
//                            print(error)
//                        }
//                        else if let string = string?.asString {
//                            print("Redis \(string)")
//                        }
//                    }
//                }
//            }
    }
    
    func get_news_feed(request: Foobar_Wall_WallQuery, session: Foobar_NewsFeedDataAccess_NewsFeedDataAccessServiceget_news_feedSession) throws -> ServerStatus? {
        var p1 = Foobar_Posts_Post()
        p1.id = 1
        p1.username = "user1"
        
        var p2 = Foobar_Posts_Post()
        p2.id = 2
        p2.username = "user2"
        
        try! session.send(p1)
        try! session.send(p2)
        session.waitForSendOperationsToFinish()

        return ServerStatus.ok
    }
    
    func add_post(request: Foobar_NewsFeedDataAccess_NewsFeedPost, session: Foobar_NewsFeedDataAccess_NewsFeedDataAccessServiceadd_postSession) throws -> Foobar_Shared_Empty {
        
        let user = request.user
        let post_id = request.post.id
        let jsonPost = try request.jsonString()
        
        let query = "INSERT INTO news_feed_data_access.nf_posts (post_id, username) VALUES (\(post_id), '\(user)');"
        self.postgres.execute(query) { (result) in
            if result.success {
                // Cache result in Redis
                // Store the key as the username, tuples are sorted by post_id
                // If the size exceeds MAX_USER_TIMELINE_CACHE_SIZE, trim the list to match
                self.redis.zadd(user, tuples: (Int(post_id), jsonPost)) { (num_elements, error) in
                    if error != nil {
                        print(error!.localizedDescription)
                    } else if (num_elements ?? 0) > self.MAX_USER_TIMELINE_CACHE_SIZE {
                        self.redis.zremrangebyrank(user, start: 0, stop: -self.MAX_USER_TIMELINE_CACHE_SIZE - 1) { (new_size, error) in
                            if error != nil {
                                print(error!.localizedDescription)
                            }
                        }
                    }
                }
            } else {
                print(result.asError!.localizedDescription)
            }
        }
        return Foobar_Shared_Empty()
    }
}


let inst = NewsFeedDataAccess(redis: Connection(host: "news_feed_data_access_redis", port: 6379),
                              psql: Connection(host: "news_feed_data_access_postgres", port: 5432))

let address = "0.0.0.0:9000"
print("Starting server in \(address)")
let server = ServiceServer(address: address,
                           serviceProviders: [inst])
server.start()
dispatchMain()
