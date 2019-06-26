import XCTest
@testable import news_feed_data_access

final class news_feed_data_accessTests: XCTestCase {
    func testExample() {
        // This is an example of a functional test case.
        // Use XCTAssert and related functions to verify your tests produce the correct
        // results.
        XCTAssertEqual(news_feed_data_access().text, "Hello, World!")
    }

    static var allTests = [
        ("testExample", testExample),
    ]
}
