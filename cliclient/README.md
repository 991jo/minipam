This directory contains the minimal cli client.

It allows you to modify everything that minipam currently offers.
for the exact commands just run it with the `--help` flag.

    python cli.py --help

If you do not want to type in the `--server` parameter all the time you can
specify it in a file called `~/minipamcli.json`. The format is as follows:

{
	"server" : "http://localhost:8000/"
}

Just adjust the server according to your setup.
