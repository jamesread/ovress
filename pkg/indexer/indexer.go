package indexer

import (
	log "github.com/sirupsen/logrus"
	"time"
	"io/ioutil"
	"os"
)

type OvressFile struct {
	Name string;
	IsDir bool;
	IsSymlink bool;
	Size int64 `yaml:",omitempty"`
	Contents map[string]OvressFile;
	FullDirectory string;

	ParentDir *OvressFile `yaml:"-"`
}

func (of *OvressFile) Dir() string {
	if of.ParentDir == nil {
		return of.Name;
	} else {
		return of.ParentDir.Dir() + "/" + of.Name
	}
}

type PathRoot struct {
	Name string;
	GeneratedDateTime string;
	Hostname string;
	Root OvressFile;
}


func scanDir(dir *OvressFile) {
	log.WithFields(log.Fields{
		"dir": dir.Name,
	}).Debugf("Scanning dir")

	files, err := ioutil.ReadDir(dir.Dir());

	if err != nil {
		log.Fatal(err)
	}

	for _, f := range files {
		log.Debug(f.Name());

		if f.IsDir() {
			odir := OvressFile {
				Name: f.Name(),
				FullDirectory: dir.Dir(),
				ParentDir: dir,
				Contents: map[string]OvressFile{},
				IsSymlink: f.Mode()&os.ModeSymlink != 0,
				IsDir: true,
			}

			if !odir.IsSymlink {
				scanDir(&odir);
			}

			dir.Contents[odir.Name] = odir;
		} else {
			ofile := OvressFile{
				Name: f.Name(),
				FullDirectory: dir.Dir(),
				ParentDir: dir,
				Size: f.Size(),
				IsSymlink: f.Mode()&os.ModeSymlink != 0,
				IsDir: false,
			}

			dir.Contents[ofile.Name] = ofile;
		}
	}
}

func ScanRoot(path string) (*PathRoot) {
	ret := PathRoot{Name: "PathRoot"};
	ret.GeneratedDateTime = time.Now().Format(time.RFC3339);
	ret.Hostname, _ = os.Hostname()
	ret.Root = OvressFile{Name: path, IsDir: true, Contents: map[string]OvressFile{}};

	scanDir(&ret.Root)

	return &ret;
}

