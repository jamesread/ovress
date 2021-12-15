package indexer

import (
	log "github.com/sirupsen/logrus"
	"time"
	"fmt"
	"compress/gzip"
	"bufio"
	"os"
	"gopkg.in/yaml.v3"
	//"encoding/json"
)

func SaveIndex(root *PathRoot) {
	log.Infof("Marshalling")

	encodedOut, err := yaml.Marshal(root)
//	encodedOut, err := json.MarshalIndent(root, "", "\t")

	if err != nil {
		log.Panicf("Panicing on yaml marshal: %v", err)
	}

	os.Mkdir(root.Root.Name + "/.ovress", 0775)

	filename := fmt.Sprintf(root.Root.Name + "/.ovress/ovress-index-%s.yaml.gz", time.Now().Format(time.RFC3339))
	
	log.WithFields(log.Fields{
		"filename": filename,
	}).Infof("Saving index file")

	fi, err := os.OpenFile(filename, os.O_WRONLY|os.O_CREATE, 0660)

	if err != nil {
		log.Panicf("Error in writing the index file %v", err)
	}

	gz := gzip.NewWriter(fi)
	fw := bufio.NewWriter(gz)
	_, err = fw.WriteString("---\n")
	_, err = fw.WriteString(string(encodedOut))

	if err != nil {
		log.Fatal(err)
	}

	fw.Flush()
	gz.Flush()
	gz.Close()

	defer fi.Close()

}

