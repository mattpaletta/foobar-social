import XCTest

#if !canImport(ObjectiveC)
public func allTests() -> [XCTestCaseEntry] {
    return [
        testCase(news_feed_mergeTests.allTests),
    ]
}
#endif
