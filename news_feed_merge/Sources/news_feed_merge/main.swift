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
    private let news_feed_data_access: Foobar_NewsFeedDataAccess_NewsFeedDataAccessServiceServiceClient!
    private let wall: Foobar_Wall_WallServiceServiceClient!
    private let posts: Foobar_Posts_PostServiceServiceClient!
    
    private let redis: Redis!
    
    private let IMPORT_QUEUE: String!
    
    init(redis: Connection) {
        let env = ProcessInfo.processInfo.environment
        guard let import_queue = env["IMPORT_QUEUE"] else {
            print("Failed to get IMPORT_QUEUE from env")
            exit(1)
        }
        print("Connecting to redis")
        self.IMPORT_QUEUE = import_queue
        self.redis = Redis()
        self.redis.connect(host: redis.host, port: redis.port) { (redisError: NSError?) in
            if let error = redisError {
                print("Failed while connecting to redis")
                print(error.localizedDescription)
                exit(1)
            }
        }
        
        self.friends = Foobar_Friends_FriendsServiceServiceClient(address: "friends:2885", secure: false, arguments: [])
        self.news_feed_data_access = Foobar_NewsFeedDataAccess_NewsFeedDataAccessServiceServiceClient(address: "news-feed-data-access:9000", secure: false, arguments: [])
        self.wall = Foobar_Wall_WallServiceServiceClient(address: "wall:4698", secure: false, arguments: [])
        self.posts = Foobar_Posts_PostServiceServiceClient(address: "posts:2885", secure: false, arguments: [])
        self.connect()
    }
    
    private func connect() {
        var counter: UInt32 = 0
        
        while self.friends.channel.connectivityState(tryToConnect: true) != .ready {
            sleep(2 * counter)
            counter += 1
            print("Connecting to friends")
        }
        
        counter = 0
        while self.news_feed_data_access.channel.connectivityState(tryToConnect: true) != .ready {
            sleep(2 * counter)
            counter += 1
            print("Connecting to news feed data access")
        }
        
        counter = 0
        while self.wall.channel.connectivityState(tryToConnect: true) != .ready {
            sleep(2 * counter)
            counter += 1
            print("Connecting to wall")
        }
        
        counter = 0
        while self.posts.channel.connectivityState(tryToConnect: true) != .ready {
            sleep(2 * counter)
            counter += 1
            print("Connecting to posts")
        }

    }
    
    public func start() {
        // Forever, try and pop message off the import queue
        // Do the fan-out to all friends in the process_message function
        while true {
            self.connect()
            print("Waiting for messages")
            self.redis.brpop(self.IMPORT_QUEUE, timeout: 0) { (value, error) in
                if error != nil {
                    print("Failure popping message")
                    print(error!.localizedDescription)
                    return
                }
                
                // Process the value
//                guard let message = value else { return }
                for item in value ?? [] {
                    if (item?.asString == "post_importer") {
                        continue
                    }
                    
                    do {
                        let post = try Foobar_Posts_Post(jsonString: item!.asString)
                        try self.process_message(post: post)
                    } catch {
                        print("Failure processing message")
                        print(error.localizedDescription)
                    }
                }
            }
        }
    }
    
    private func process_message(post: Foobar_Posts_Post) throws {
        var user = Foobar_User_User()
        user.username = post.username
        var isDone = false
        print("Getting friends iterator")
        print(user)
        let userFriends = try self.friends.get_friends(user) { (result) in
            if !result.success {
                print("Failed to get friends")
                print(result.statusMessage!)
            }
            isDone = true
        }
        
        var friendUsernames: [String] = []
        
        print("Waiting until done getting friends")
        while !isDone {
            do {
                let nextFriend = try userFriends.receive()
                print("Received friend")
                guard let nextUsername = nextFriend?.username else {
                    print("Skipping friends")
                    continue
                }
                friendUsernames.append(nextUsername)
            } catch {
                print("Failed retrieving friend")
                print(error.localizedDescription)
            }
        }
        
        // Post to the posts db first, then to the wall
        print(try! post.jsonString())
        print("Sending to posts")
        let _ = try self.posts.create_post(post)
        print("Sending to wall")
        let _ = try self.wall.put(post)
        
        // Finally, we distribute on news feeds
        print("Getting queue and group")
        let queue = DispatchQueue(label: "submit_friends")
        let group = DispatchGroup()
        
        print("Distributing message")
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
                    print("Failed to add to news feed data access")
                    print(error.localizedDescription)
                }
            }
        }
        
        group.wait()
        print("Finished processing messages")
    }
}

let num_servers = 10
print("Starting \(num_servers) servers")

for _ in 0 ..< num_servers {
    DispatchQueue.global(qos: .default).async {
        let server = NewsFeedMerge(redis: Connection(host: "post-importer-redis", port: 6379))
        server.start()
    }
}

dispatchMain()
