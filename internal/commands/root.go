package commands

import (
	"fmt"
	"os"

	"github.com/spf13/cobra"
)

var rootCmd = &cobra.Command{
	Use:   "ovress",
	Short: "Ovress is a service to track file replication",
	Long:  "Ovress is a service to track file replication. http://github.com/jamesread/ovress/",
}

func ExecuteRoot() {
	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
