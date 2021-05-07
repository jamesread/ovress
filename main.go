package main

import (
	"github.com/jamesread/ovress/cmd"
	log "github.com/sirupsen/logrus"
)

func main() {
	log.Info("ovress")

	cmd.Execute()
}
