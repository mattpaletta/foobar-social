PROTO_DIR := ./protos

PYDIR := MY_DIR
PYPROTOC := python3 -m grpc_tools.protoc -I./$(PROTO_DIR) --python_out=./MY_DIR/  --grpc_python_out=./MY_DIR/ --mypy_out=./MY_DIR
SWIFTPROTOC := protoc -I ./$(PROTO_DIR) --swiftgrpc_out=./MY_DIR/Sources/MY_DIR/protos --swift_out=./MY_DIR/Sources/MY_DIR/protos
PHPPROTOC := protoc -I ./$(PROTO_DIR) --plugin=protoc-gen-grpc=/home/jacob/.grpc/bins/grpc_php_plugin  --php_out=./MY_DIR/src/ --grpc_out=./MY_DIR/src/ 
EXTRACT_IMPORTS := 's/^import\ "\([a-zA-Z]*.proto\)";/\1/p'
EXTRACT_IMPORT_BASE := 's/^import\ "\([a-zA-Z]*\).proto";/\1/p'

define get_imports_sub
	$(call get_imports,$1.proto)
endef

define get_imports
	$(patsubst %, $(PROTO_DIR)/%, $(shell sed -n $(EXTRACT_IMPORTS) protos/${1}.proto ))
endef

define get_outputs
	${2}/${1}_pb2.py ${2}/${1}_pb2_grpc.py ${2}/${1}_pb2.pyi
endef

define generate_protos
	@echo Generating Protos $1... \
	$(shell $(subst $(PYDIR),${2},$(3)) $1.proto) \
	$(foreach cur_file,$(call get_imports,$1), \
		$(shell $(subst $(PYDIR),$(2),$(3)) $(cur_file)) \
	)
endef

define generate_protos_py
	$(call generate_protos,$1,$2,${PYPROTOC})
endef

define generate_protos_py_unary
	$(call generate_protos_py,$1,$1)
endef

define generate_protos_swift
	$(call generate_protos,$1,$2,${SWIFTPROTOC})
endef

define generate_protos_PHP
	$(call generate_protos,$1,$2,${PHPPROTOC})
endef


auth := $(call get_outputs,auth,auth)
$(auth):
	$(call generate_protos_py_unary,auth)
	$(call generate_protos_py,token,auth)
	$(call generate_protos_py,user_setting,auth)
auth: $(auth)

apilayer: $(PROTO_DIR)/*.proto
	cp -r protos/ apilayer/src/main/proto
create_user := $(call get_outputs,create_user,create_user)
$(create_user):
	$(call generate_protos_py_unary,create_user)
	$(call generate_protos_py,token,create_user)
	$(call generate_protos_py,users,create_user)
create_user: $(create_user)
client:
	$(call generate_protos_py,apilayer,client)
	$(call generate_protos_py,user,client)
	$(call generate_protos_py,shared,client)
	docker-compose up --build -d client && docker run -it --rm --net foobar-social_default foobar-social_client:latest

friends := $(call get_outputs,friends,friends)
$(friends):
	$(call generate_protos_py_unary,friends)
friends: $(friends)

news_feed := $(call get_outputs,news_feed,news_feed)
$(news_feed):
	cp protos/news_feed.proto news_feed/news_feed.proto
	cp protos/wall.proto news_feed/wall.proto
	cp protos/posts.proto news_feed/posts.proto
	cp protos/user.proto news_feed/user.proto
	cp protos/shared.proto news_feed/shared.proto
	cp protos/news_feed_data_access.proto news_feed/news_feed_data_access.proto

news_feed: $(news_feed)

news_feed_merge: friends profile news_feed_data_access
	$(call generate_protos_swift,friends,news_feed_merge)
	$(call generate_protos_swift,profile,news_feed_merge)
	$(call generate_protos_swift,wall,news_feed_merge)
	$(call generate_protos_swift,posts,news_feed_merge)
	$(call generate_protos_swift,news_feed_data_access,news_feed_merge)

news_feed_data_access := $(call get_outputs,news_feed_data_access,news_feed_data_access)
$(news_feed_data_access):
	$(call generate_protos_swift,news_feed_data_access,news_feed_data_access)
	$(call generate_protos_swift,user,news_feed_data_access)

news_feed_data_access: $(news_feed_data_access)

post_importer := $(call get_outputs,post_importer,post_importer)
$(post_importer):
	$(call generate_protos_swift,post_importer,post_importer)

post_importer: $(post_importer)

posts := $(call get_outputs,posts,posts)
$(posts):
	$(call generate_protos_py_unary,posts)
posts: $(posts)

profile := $(call get_outputs,profile,profile)
$(profile):
	$(call generate_protos_py_unary,profile)
profile: $(profile)

token := $(call get_outputs,token,token_dispenser)
$(token):
	$(call generate_protos_py,token,token_dispenser)
token: $(token)

users := $(call get_outputs,users,users)
$(users):
	$(call generate_protos_py_unary,users)
	$(call generate_protos_py,user,users)
	$(call generate_protos_py,auth,users)
users: $(users)

user_setting := $(call get_outputs,user_setting,user_setting)
$(user_setting):
	$(call generate_protos_py_unary,user_setting)
user_setting: $(user_setting)

wall := $(call get_outputs,wall,wall)
$(wall):
	$(call generate_protos_py_unary,wall)
wall: $(wall)

web_client:
	$(call generate_protos_PHP,apilayer,web_client)
	$(call generate_protos_PHP,auth,web_client)
	$(call generate_protos_PHP,posts,web_client)
	$(call generate_protos_PHP,wall,web_client)

tester: protos/*.proto
	find protos -name "*.proto" -exec sh -c "python3 -m grpc_tools.protoc -I./protos --python_out=./tester/  --grpc_python_out=./tester/ --mypy_out=./tester {}" \;

clean:
	rm -rf **/*_pb2.pyi **/*_pb2.py **/*_pb2_grpc.py **/*grpc.swift **/*pb.swift

all: apilayer auth create_user friends news_feed news_feed_merge news_feed_data_access post_importer posts profile token  users user_setting wall tester
