#ifndef _CONFIG_H_
#define _CONFIG_H_

#define CGI_PATTERN "/cgi-bin/*"
#define CGI_TIMELIMIT 30
#define IDLE_READ_TIMELIMIT 60
#define IDLE_SEND_TIMELIMIT 300
#define LOG_FACILITY LOG_DAEMON
#define TILDE_MAP_2 "public_html"
#define AUTH_FILE ".htpasswd"
#define DEFAULT_CHARSET "iso-8859-1"
#define ALWAYS_VHOST
#define DEFAULT_USER "http"
#define EXPLICIT_ERROR_PAGES
#define ERR_DIR "errors"
#define ERR_APPEND_SERVER_INFO
#define CGI_NICE 10
#define CGI_PATH "/usr/local/bin:/bin:/usr/bin"
#define OCCASIONAL_TIME 300
#define STATS_TIME 3600
#define MIN_REAP_TIME 30
#define MAX_REAP_TIME 900

#define CGI_BYTECOUNT 50000
#define DEFAULT_PORT 80
#define INDEX_NAMES "index.html", "index.htm", "index.cgi"
#define GENERATE_INDEXES
#define THROTTLE_TIME 300
#define LISTEN_BACKLOG 1024
#define MAXTHROTTLENUMS 10
#define SPARE_FDS 10
#define LINGER_TIME 2
#define MAX_LINKS 32
#define MIN_WOULDBLOCK_DELAY 100L

#endif
