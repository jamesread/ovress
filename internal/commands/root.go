package commands

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"

	log "github.com/sirupsen/logrus"
)

var rootCmd = &cobra.Command{
	Use:   "ovress",
	Short: "Ovress is a service to track file replication",
	Long:  "Ovress is a service to track file replication. http://github.com/jamesread/ovress/",
}

var logLevelString string;

func init() {
	rootCmd.PersistentFlags().StringVar(&logLevelString, "logLevel", "info", "The log level")
}

func setupLogLevel() {
	log.SetFormatter(&log.TextFormatter{
		DisableColors: false,
		DisableTimestamp: true,
	})

	lvl, err := log.ParseLevel(logLevelString)

	if err != nil {
		log.Fatal(err)
	} else {
		log.Infof("Setting log level to: %v", lvl)
		log.SetLevel(lvl)
	}
}

func ExecuteRoot() {
	cobra.OnInitialize(setupLogLevel)

	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
