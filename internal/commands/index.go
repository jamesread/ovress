package commands

import (
	"bufio"
	"os"
	"gopkg.in/yaml.v3"
	"compress/gzip"
	"fmt"
	"time"

	log "github.com/sirupsen/logrus"

	"github.com/jamesread/ovress/pkg/indexer"

	"github.com/spf13/cobra"
)

func getIndexCmd() *cobra.Command {
	var indexCmd = &cobra.Command{
		Use:   "index",
		Short: "Indexes a file path",
		Long: `A longer description that spans multiple lines and likely contains examples
	and usage of using your command. For example:

	Cobra is a CLI library for Go that empowers applications.
	This application is a tool to generate the needed files
	to quickly create a Cobra application.`,
		Run: func(cmd *cobra.Command, args []string) {
			path, _ := cmd.Flags().GetString("path")

			runIndex(path) // FIXME
			log.Info("Indexing complete");
		},
	}

	indexCmd.Flags().String("path", ".", "The path (directory) to index")

	return indexCmd
}

func runIndex(path string) {
	log.WithFields(log.Fields{
		"path": path,
	}).Infof("Indexing starting")

	root := indexer.ScanRoot(path)

	saveIndex(root)

	log.WithFields(log.Fields{
		"path": path,
	}).Infof("Indexing complete")

}

func saveIndex(root *indexer.PathRoot) {
	yamlOut, err := yaml.Marshal(root)

	if err != nil {
		log.Error(err)
	}

	filename := fmt.Sprintf(".ovress/ovress-index-%s.yaml.gz", time.Now().Format(time.RFC3339))

	fi, err := os.OpenFile(filename, os.O_WRONLY|os.O_CREATE, 0660)

	if err != nil {
		log.Panicf("Error in writing the index file %v", err)
	}

	gz := gzip.NewWriter(fi)
	fw := bufio.NewWriter(gz)
	_, err = fw.WriteString(string(yamlOut))

	if err != nil {
		log.Fatal(err)
	}

	fw.Flush()
	gz.Flush()
	gz.Close()

	defer fi.Close()
}

func init() {
	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	rootCmd.AddCommand(getIndexCmd())

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// indexCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
