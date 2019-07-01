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

class NewsFeedMerge {
    
    private let friends: Foobar_Friends_FriendsServiceServiceClient!
    private let news_feed_data_access: Foobar_NewsFeedDataAccess_NewsFeedDataAccessServiceServiceClient
    private let redis: Redis!
    
    private let IMPORT_QUEUE: String!
    
    init(redis: Connection) {
        let env = ProcessInfo.processInfo.environment
        guard let import_queue = env["IMPORT_QUEUE"] else {
            print("Failed to get IMPORT_QUEUE from env")
            exit(1)
        }
        
        self.IMPORT_QUEUE = import_queue
        self.redis = Redis()
        self.redis.connect(host: redis.host, port: redis.port) { (redisError: NSError?) in
            if let error = redisError {
                print(error)
                exit(1)
            }
        }
        
        self.friends = Foobar_Friends_FriendsServiceServiceClient(address: "friends:1023", secure: false, arguments: [])
        self.news_feed_data_access = Foobar_NewsFeedDataAccess_NewsFeedDataAccessServiceServiceClient(address: "news_feed_data_access", secure: false, arguments: [])
    }
    
    public func start() {
        // Forever, try and pop message off the import queue
        // Do the fan-out to all friends in the process_message function
        while true {
            self.redis.brpop(self.IMPORT_QUEUE, timeout: 0) { (value, error) in
                if error != nil {
                    print(error!.localizedDescription)
                    return
                }
                
                // Process the value
                guard let message = value else { return }
                for item in message {
                    do {
                        let post = try Foobar_Posts_Post(jsonString: item!.asString)
                        try self.process_message(post: post)
                    } catch {
                        print(error)
                        return
                    }
                }
            }
        }
    }
    
    private func process_message(post: Foobar_Posts_Post) throws {
        var user = Foobar_User_User()
        user.username = post.username
        var isDone = false
        let userFriends = try self.friends.get_friends(user) { (result) in
            if !result.success {
                print(result.statusMessage!)
            }
            isDone = true
        }
        
        var friendUsernames: [String] = []
        
        while !isDone {
            let nextFriend = try userFriends.receive()
            guard let nextUsername = nextFriend?.username else { continue }
            friendUsernames.append(nextUsername)
        }
        
        let queue = DispatchQueue(label: "submit_friends")
        let group = DispatchGroup()
        
        for friend in friendUsernames {
            queue.async {
                defer {
                    group.leave()
                }
                group.enter()
                var newsPost = Foobar_NewsFeedDataAccess_NewsFeedPost()
                newsPost.user = friend
                newsPost.post = post
                do {
                    let _ = try self.news_feed_data_access.add_post(newsPost)
                } catch {
                    print(error)
                }
            }
        }
        
        group.wait()
    }
}


let server = NewsFeedMerge(redis: Connection(host: "post_importer_redis", port: 6379))
server.start()
dispatchMain()
