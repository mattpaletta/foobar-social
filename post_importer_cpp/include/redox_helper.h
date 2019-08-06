//
// Created by Matthew Paletta on 2019-07-26.
//

#ifndef REDOX_HELPER_H
#define REDOX_HELPER_H
#include <string>
#include <iostream>
#include <sstream>
#include <chrono>
#include <thread>
#include <cmath>

#include "redox.hpp"


// https://github.com/IBM-Swift/Kitura-redis/blob/master/Sources/SwiftRedis/Redis%2BBasic.swift

class Redis {
public:
    Redis(const std::string& host, const int& port = 6379) : rdx() {
        // Does not sleep the event loop
        // Better performance, higher CPU
        //this->rdx.noWait(true);

        int maxRetries = 10;

        bool did_connect = false;
        for (int curRetry = 0; curRetry < maxRetries && !did_connect; ++curRetry) {
            did_connect = this->rdx.connect(host, port);
            // Exponential backoff between retries
            std::this_thread::sleep_for(std::chrono::seconds(std::size_t(std::pow<long double>(2, curRetry))));
        }
        // If we went through all the retries, and we still haven't connected, throw an error.
        if (!did_connect) {
            throw std::runtime_error("Unable to connect to redis host");
        }
    }

    std::string get(const std::string& key) {
        return this->rdx.get(key);
    }

    bool set(const std::string& key, const std::string& value) {
        return this->rdx.set(key, value);
    }

    bool del(const std::string& key) {
        return this->rdx.del(key);
    }

    std::size_t incr(const std::string& key, const std::size_t amount = 1) {
        const auto& string = this->run_wait_cmd({"INCRBY", key, std::to_string(amount)});
        std::stringstream sstream(string);
        std::size_t result;
        sstream >> result;
        return result;
    }

    std::string blpop(const std::string& key, const std::size_t& timeout = 0) {
        return this->block_helper("BLPOP", key, timeout);
    }

    std::string brpop(const std::string& key, const std::size_t& timeout = 0) {
        return this->block_helper("BRPOP", key, timeout);
    }

    std::string brpoplpush(const std::string& src, const std::string& dest, const std::size_t& timeout = 0) {
        return this->run_wait_cmd({"BRPOPLPUSH", src, dest, std::to_string(timeout)});
    }

    void lpush(const std::string& queue, const std::string& value) {
        auto& cmd = this->rdx.commandSync<std::string>({"LPUSH", queue, value});
        cmd.free();
    }

    void lpush(const std::string& queue, const std::vector<std::string>& values) {
        std::vector<std::string> vec;
        vec.emplace_back("LPUSH");
        vec.push_back(queue);
        vec.insert(vec.end(), values.begin(), values.end());
        auto& cmd = this->rdx.commandSync<std::string>(std::move(vec));
        cmd.free();
    }

    void rpush(const std::string& queue, const std::string& value) {
        auto& cmd = this->rdx.commandSync<std::string>({"RPUSH", queue, value});
        cmd.free();
    }

    void rpush(const std::string& queue, const std::vector<std::string>& values) {
        std::vector<std::string> vec;
        vec.emplace_back("RPUSH");
        vec.push_back(queue);
        vec.insert(vec.end(), values.begin(), values.end());
        auto& cmd = this->rdx.commandSync<std::string>(std::move(vec));
        cmd.free();
    }

private:
    redox::Redox rdx;

    std::string block_helper(const std::string& redis_cmd, const std::string& key, const std::size_t& timeout = 0) {
        return this->run_wait_cmd({redis_cmd, key, std::to_string(timeout)});
    }

    std::string run_wait_cmd(const std::vector<std::string>& redis_cmd) {
        auto& cmd = this->rdx.commandSync<std::string>(redis_cmd);
        auto reply = cmd.reply();
        cmd.free();
        return reply;
    }
};

//Redis getClient(const std::string& host, const int& port) {
//    return Redis(host, port);
//}

#endif