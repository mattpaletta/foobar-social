import XCTest

#if !canImport(ObjectiveC)
public func allTests() -> [XCTestCaseEntry] {
    return [
        testCase(news_feed_data_accessTests.allTests),
    ]
}
#endif
