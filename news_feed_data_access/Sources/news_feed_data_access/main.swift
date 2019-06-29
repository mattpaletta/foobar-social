import Dispatch
import SwiftGRPC

class NewsFeedDataAccess : Foobar_NewsFeedDataAccess_NewsFeedDataAccessServiceProvider {
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


let inst = NewsFeedDataAccess()

let address = "0.0.0.0:9000"
print("Starting server in \(address)")
let server = ServiceServer(address: address,
                           serviceProviders: [NewsFeedDataAccess()])
server.start()
dispatchMain()
