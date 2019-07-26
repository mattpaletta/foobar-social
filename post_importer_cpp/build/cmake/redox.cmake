include(ExternalProject)

set(REDOX_DOWNLOAD_ROOT ${CMAKE_BINARY_DIR}/redox)
set(HIREDIS_DOWNLOAD_ROOT ${CMAKE_BINARY_DIR}/hiredis)
set(LIBEV_DOWNLOAD_ROOT ${CMAKE_BINARY_DIR}/libev)

ExternalProject_Add(
        libev
        SOURCE_DIR "${LIBEV_DOWNLOAD_ROOT}/libev-src"
        BINARY_DIR "${LIBEV_DOWNLOAD_ROOT}/libev-build"
        GIT_REPOSITORY https://github.com/LuaDist/libev.git
        BUILD_ALWAYS OFF
        #        CONFIGURE_COMMAND ""
        #        BUILD_COMMAND ""
        #        INSTALL_COMMAND ""
        #        TEST_COMMAND ""
)

ExternalProject_Add(
        hiredis
        SOURCE_DIR "${HIREDIS_DOWNLOAD_ROOT}/hiredis-src"
        BINARY_DIR "${HIREDIS_DOWNLOAD_ROOT}/hiredis-build"
        GIT_REPOSITORY https://github.com/redis/hiredis.git
        BUILD_ALWAYS OFF
#        INSTALL_DIR "${HIREDIS_DOWNLOAD_ROOT}/hiredis"
        #        CONFIGURE_COMMAND ""
#                BUILD_COMMAND ""
        #        INSTALL_COMMAND ""
        #        TEST_COMMAND ""
)

ExternalProject_Add(
        redox
        SOURCE_DIR "${REDOX_DOWNLOAD_ROOT}/redox-src"
        BINARY_DIR "${REDOX_DOWNLOAD_ROOT}/redox-build"
        GIT_REPOSITORY https://github.com/hmartiro/redox.git
        GIT_TAG b5b9fa31a6fba3f7ce872e623958cb27b7686039
        BUILD_ALWAYS OFF
#        -Dhiredis_DIR:PATH=${HIREDIS_DOWNLOAD_ROOT}/hiredis-build
#        CONFIGURE_COMMAND ""
#        BUILD_COMMAND ""
#        INSTALL_COMMAND ""
#        TEST_COMMAND ""
#        HIREDIS_PATH ${HIREDIS_DOWNLOAD_ROOT}/hiredis-build
#        DEPENDS hiredis libev
)
#add_dependencies(redox hiredis)