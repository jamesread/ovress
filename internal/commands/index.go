package commands

import (
	log "github.com/sirupsen/logrus"

	"github.com/jamesread/ovress/pkg/indexer"

	"github.com/spf13/cobra"
)

func newIndexCmd() *cobra.Command {
	var indexCmd = &cobra.Command{
		Use:   "index",
		Short: "Indexes a file path",
		Run: runIndexCmd,
		Args: cobra.MinimumNArgs(1),
	}

	return indexCmd
}

func runIndexCmd(cmd *cobra.Command, args []string) {
	for _, path := range args {
		log.WithFields(log.Fields{
			"path": path,
		}).Infof("Indexing starting")

		root := indexer.ScanRoot(path)
		indexer.SaveIndex(root)

		log.WithFields(log.Fields{
			"path": path,
		}).Infof("Indexing complete")
	}
}

func init() {
	rootCmd.AddCommand(newIndexCmd())
}
