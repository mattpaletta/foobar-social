token: protos/token.proto protos/auth.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./token_dispenser/ --mypy_out=./token_dispenser auth.proto
	python3 -m grpc_tools.protoc -I./protos --python_out=./token_dispenser/ --grpc_python_out=./token_dispenser/ --mypy_out=./token_dispenser token.proto