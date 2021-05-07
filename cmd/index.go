package cmd

import (
	"bufio"
	"os"
	"encoding/json"
	"compress/gzip"
	"strings"
	"fmt"
	"time"

	log "github.com/sirupsen/logrus"

	"github.com/jamesread/ovress/pkg/indexer"

	"github.com/spf13/cobra"
)

var indexCmd = &cobra.Command{
	Use:   "index",
	Short: "A brief description of your command",
	Long: `A longer description that spans multiple lines and likely contains examples
and usage of using your command. For example:

Cobra is a CLI library for Go that empowers applications.
This application is a tool to generate the needed files
to quickly create a Cobra application.`,
	Run: func(cmd *cobra.Command, args []string) {
		path := strings.Join(args, " ")

		runIndex(path) // FIXME
		log.Info("Indexing complete");
	},
}

func runIndex(path string) {
	log.Infof("Indexing %s", path);

	root := indexer.ScanRoot(path)

	jsonOut, err := json.MarshalIndent(root, "", " ")

	if err != nil {
		log.Error(err)
	}

	filename := fmt.Sprintf("ovress-index-%s.json.gz", time.Now().Format(time.RFC3339))

	fi, err := os.OpenFile(filename, os.O_WRONLY|os.O_CREATE, 0660)

	if err != nil {
		log.Panicf("Error in writing the index file %v", err)
	}

	gz := gzip.NewWriter(fi)
	fw := bufio.NewWriter(gz)
	fw.WriteString(string(jsonOut))
}

func init() {
	rootCmd.AddCommand(indexCmd)

	// Here you will define your flags and configuration settings.

	// Cobra supports Persistent Flags which will work for this command
	// and all subcommands, e.g.:
	indexCmd.Flags().String("path", "", "The path (directory) to index")
//	indexCmd.MarkFlagRequired("path");

	// Cobra supports local flags which will only run when this command
	// is called directly, e.g.:
	// indexCmd.Flags().BoolP("toggle", "t", false, "Help message for toggle")
}
