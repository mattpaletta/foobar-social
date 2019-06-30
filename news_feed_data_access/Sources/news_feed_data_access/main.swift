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
    
    func add_post(request: Foobar_Posts_Post, session: Foobar_NewsFeedDataAccess_NewsFeedDataAccessServiceadd_postSession) throws -> Foobar_Shared_Empty {
        print("Got Post: \(request.msg))")
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
