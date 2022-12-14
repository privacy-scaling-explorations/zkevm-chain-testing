#!/bin/bash
set -e
set -x

go mod init zkevmchaintest
go mod tidy
#go get -u github.com/ethereum/go-ethereum
#cd /go/pkg/mod/github.com/ethereum/go-ethereum\@v1.10.18/
#make devtools 