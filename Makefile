auth: protos/auth.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./auth/  --grpc_python_out=./auth/ --mypy_out=./auth auth.proto

friends: profile protos/friends.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./friends/ --mypy_out=./friends profile.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./friends/  --grpc_python_out=./friends/ --mypy_out=./friends friends.proto

profile: protos/friends.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./profile/  --grpc_python_out=./profile/ --mypy_out=./profile profile.proto

news_feed: protos/news_feed.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./news_feed/  --grpc_python_out=./news_feed/ --mypy_out=./news_feed news_feed.proto

news_feed_data_access: protos/news_feed_data_access.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./news_feed_data_access  --grpc_python_out=./news_feed_data_access --mypy_out=./news_feed_data_access news_feed_data_access.proto

post_importer: protos/post_importer.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./post_importer  --grpc_python_out=./post_importer --mypy_out=./post_importer post_importer.proto

posts: protos/posts.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./posts  --grpc_python_out=./posts --mypy_out=./posts posts.proto

profile: protos/profile.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./profile  --grpc_python_out=./profile --mypy_out=./profile profile.proto

token: protos/token.proto auth
	python3 -m grpc_tools.protoc -I./protos --python_out=./token_dispenser/ --mypy_out=./token_dispenser auth.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./token_dispenser/ --grpc_python_out=./token_dispenser/ --mypy_out=./token_dispenser token.proto

user_setting: protos/user_setting.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./user_setting --grpc_python_out=./user_setting --mypy_out=./user_setting user_setting.proto

wall: protos/wall.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./wall --grpc_python_out=./wall --mypy_out=./wall wall.proto
